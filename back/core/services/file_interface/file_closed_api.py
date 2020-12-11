import logging

from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.file_related_model import FileRelatedModelApi
from core.services.git_interface.git_interface import GitInterface
from core.services.file_interface.file_find_item import FileItemsFinder
from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_row import LocalizeRowReader
from core.services.file_interface.file_read_ue import LocalizeUEReader
from core.services.file_interface.file_scanner import FileScanner

from core.models import Translate, File, Translated, MarkItem, ErrorFiles, Language

logger = logging.getLogger('django')


class FileClosedApi:
    """ Api with file model and sub models(file-mark-item-translate-log) """

    def __init__(self, file_id: int):
        """ Get file object from database to do other actions """
        # Object flags and params
        self._log_name = ''
        # Init
        try:
            # self._file = File.objects.select_related('lang_orig').get(id=file_id)
            self._file = File.objects.get(id=file_id)
            # TODO: Save file params to class params that used
        except ObjectDoesNotExist:
            self._handle_err(f"File not found ID: {file_id}")
        except Exception as exc:
            self._handle_err(f"Unknown exception while getting file object. ID: {file_id} exception: {exc}", 2)
        else:
            # Object flags and params
            # self._lang_orig = self._file.lang_orig
            self._log_name = f'{self._file.name}(id:{self._file.id})'
            self._structure_changed = False   # Flag to check if file structure have changed

    def _file_refresh(self, tmp_path: str, lang_id: int, is_original: bool) -> bool:
        """ File refresh translates (mark-item-translate) for selected language """
        current_options = self._file.options
        lang_short_name = _ClassUtil.get_lang_short_name(lang_id)
        info = FileScanner(tmp_path, lang_short_name)
        """ Phase 0: Delete progress for new original (then refresh if no errors) """
        if is_original:
            self._file.translated_set.all().delete()
        """ Phase 1: Check info for critical errors """
        if info.error:
            if is_original:
                self._handle_err(f"get info error:{info.error}")
                self._file.error = info.error
                self._file.save()
            else:
                self._handle_err(f"Uploaded {tmp_path} file get info error:{info.error}")
                settings.STORAGE_ERRORS.delete(tmp_path)
            return False
        """ Phase 2: Check file if structure change (new = true) """
        if current_options != info.options:
            logger.info(f'Loaded file {tmp_path} structure not same as was before for {self._log_name}')
            if is_original:
                self._structure_changed = True
            else:
                self._handle_err("Can't fill translates if structure not same")
                settings.STORAGE_ERRORS.delete(tmp_path)
                return False
        """ Phase 3: Update structure if upload file is original language """
        logger.info(f"File {self._log_name} get info success - method:{info.method}")
        if is_original and self._structure_changed:
            logger.info(f"File {self._log_name} uploaded new original with changed structure:{info.options}")
            self._file.codec = info.codec
            self._file.method = info.method
            self._file.options = info.options
        """ Phase 4: Rebuild file """
        if is_original:
            languages = self.__file_progress_create()
            try:
                logger.info(f'File {self._log_name} try build marks as original')
                self.__file_rebuild_original(lang_id, languages, info)  # file.save() called if success
            except AssertionError as err:
                self._handle_err("File {} build marks error: " + str(err))
                self._file.error = err
                self._file.save()
                return False
            else:
                """ Phase 5: Refresh progress """
                self.__file_progress_refresh_all()
        else:
            logger.info(f'File {self._log_name} try build marks for language {lang_id}')
            try:
                self.__file_rebuild_translates(lang_id, info)
            except AssertionError as err:
                self._handle_err("File {} build translates error: " + str(err))
            finally:
                """ Phase 5: Refresh progress and del tmp data """
                settings.STORAGE_ERRORS.delete(tmp_path)
                self._file_progress_refresh(lang_id)
        return True

    def __file_rebuild_original(self, orig_id: int, languages_to: list[int], info_obj: FileScanner):
        """ Update, delete, insert translates while parsing file -> then refresh file stats """
        if not _ClassUtil.fid_lookup_formula_exist(info_obj):
            logger.info(f'File {self._log_name} don\'t have fID formula and will build by index')

        reader = _ClassUtil.get_reader(info_obj)
        finder = FileItemsFinder(self._file.id)  # Prepare finder and remember old marks
        for file_mark in reader:
            model_api = FileRelatedModelApi(orig_id, languages_to)  # Api to work with models
            # Getting FileMark object
            mark = model_api.mark_create_or_update(self._file.id, file_mark)
            # Add mark id not to delete
            finder.used_mark_id = mark.pk

            numbers_not_to_delete: list[int] = []  # After adding MarkItems - delete old unused
            for mark_item in file_mark['items']:
                numbers_not_to_delete.append(mark_item['item_number'])
                # Prepare translates to find by inner text (old translates in DB)
                translates_with_text = finder.find_by_md5(mark_item['md5sum'])
                # Create or update MarkItem and it's Translates
                model_api.item_refresh(mark.pk, mark_item, translates_with_text)
            # Delete old MarkItems for Mark
            delete_amount, _ = mark.markitem_set.exclude(item_number__in=numbers_not_to_delete).delete()
            if delete_amount and not self._structure_changed:  # Can not be new items if structure don't change
                self._handle_err(f'structure not changed but was {delete_amount} items to delete', 2)
        # Delete unused Marks
        _amount, _ = self._file.filemark_set.exclude(id__in=finder.used_mark_id).delete()
        logger.info(f"File {self._log_name} delete {_amount} unused marks")
        # Save results
        self._file.error = ''
        self._file.items, self._file.words = reader.stats
        self._file.save()
        logger.info(f"File {self._log_name} build as original success")

    def __file_rebuild_translates(self, lang_id, info_obj):
        """ Update, delete, insert translates while parsing file for selected language then update progress """
        if _ClassUtil.fid_lookup_formula_exist(info_obj):
            warning = ''
        else:
            warning = 'translate placed by file index'  # TODO: It ok to change translate without formula ?
            self._handle_err('translate copy don\'t have fID formula and will build by index')

        reader = _ClassUtil.get_reader(info_obj)
        for file_mark in reader:
            try:
                mark = self._file.filemark_set.get(fid=file_mark['fid'])
            except ObjectDoesNotExist:
                continue
            else:
                model_api = FileRelatedModelApi()
                for mark_item in file_mark['items']:
                    if not model_api.translate_update_or_err(mark.pk, lang_id, mark_item, warning):
                        self._handle_err(f"can't find translate for fID:{file_mark['fid']} to fill language:{lang_id}")
        logger.info(f"File {self._log_name} build as copy success")

    def _file_progress_refresh(self, lang_id):
        """ Refresh file progress for language """
        try:
            progress = self._file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            self._handle_err(f'related translated object not found for language:{lang_id}', 2)
            return False
        translated_items_amount = MarkItem.objects.filter(mark__file_id=self._file.id) \
            .filter(Q(translate__language=lang_id), ~Q(translate__text__exact="")).count()
        progress.items = translated_items_amount
        progress.need_refresh = True   # When progress need_refresh - mark to create new translated copy
        progress.save()
        logger.info(f"File {self._log_name} progress refresh for language:{lang_id}")
        if self._file.items != translated_items_amount:
            if self._file.items < translated_items_amount:
                self._handle_err("For file {} translates items:" + translated_items_amount + " more then file have", 2)
            return False
        return True

    def __file_progress_refresh_all(self):
        """ Refresh file progress for all languages """
        for translated in self._file.translated_set.all():
            self._file_progress_refresh(translated.language)

    def __file_progress_create(self):
        """ Create progress for 'new' file """
        logger.info(f"File {self._log_name} creating progress for all languages")
        translate_to_ids = [x for x in self._file.folder.project.translate_to.values_list('id', flat=True)]
        objects_to_create = [Translated(file_id=self._file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objects_to_create)
        return translate_to_ids

    def _translate_copy_create(self, lang_to_id: int) -> None:
        """ Create translation copy of the file to selected language """
        original_file_path = self._file.data.path
        info = FileScanner(path=original_file_path)  # Fixme - get info from db_model
        lang_short_name = _ClassUtil.get_lang_short_name(lang_to_id)
        copy_path = CopyContextControl.get_path(original_file_path, lang_short_name)
        if not copy_path:
            copy_path = CopyContextControl.get_path(original_file_path, lang_short_name)
        reader = _ClassUtil.get_reader(info_obj=info, copy_path=copy_path)

        for file_mark in reader:
            mark_translates = Translate.objects\
                .filter(item__mark__file__id=self._file.id, language_id=lang_to_id, item__mark__fid=file_mark['fid'])\
                .exclude(text__exact="").values('item__item_number', 'text')
            # Remap items as {item_number: xx, text: yy}
            mark_translates = [{'item_number': tr['item__item_number'], 'text': tr['text']} for tr in mark_translates]
            # if file_mark['fid'] in tr_items:
            reader.copy_write_mark_items(mark_translates)
        # Update model as finished
        progress = self._file.translated_set.get(language_id=lang_to_id)
        progress.translate_copy = copy_path
        progress.need_refresh = False   # Set status - copy refreshed
        progress.save()

    def _translate_copy_upload_in_repo(self, lang_id: int) -> bool:
        """ Update file translated copy in repository """
        # TODO: Make choices how to save copy in repo (EN/filename.txt or filename-en.txt)
        if self._file.folder.repo_status:
            copy = self._file.translated_set.get(language_id=lang_id)
            git_manager = GitInterface()
            try:
                git_manager.repo = model_to_dict(self._file.folder.folderrepo)
                new_file_sha, err = git_manager.upload_file(copy.translate_copy.path, copy.repo_sha)
            except AssertionError as err:
                self._handle_err(f"can't set repository: {err}")
                return False
            if err:
                self._handle_err(f"error uploading copy to lang {lang_id} - {err}")
                return False
            copy.repo_hash = new_file_sha
            copy.save()
            logger.info(f"Success uploaded file copy {self._log_name} for lang {lang_id} to repository")
            return True
        else:
            logger.info(f"Folder repository not found for file {self._log_name}")
        return False

    def _file_download_from_repo(self):
        """ Update file from git repository """
        if self._file.folder.repo_status:
            self._file.repo_status = False
            logger.info(f"File {self._log_name} trying to update from repository - set status False (not found)")
            # Get list of updated files from git
            git_manager = GitInterface()
            try:
                git_manager.repo = model_to_dict(self._file.folder.folderrepo)
                new_sha, err = git_manager.update_file(self._file.data.path, self._file.repo_sha)
            except AssertionError as error:
                self._handle_err(f"can't set repository error: {error}", 1)
            else:
                if err:
                    self._handle_err(f'update from repository error: {err}')
                elif new_sha:
                    logger.info(f"File {self._log_name} updated from repository - set status True (found)")
                    self._file.repo_status = True
                    self._file.repo_sha = new_sha
                else:  # If not set - file not updated in repository
                    logger.info(f"File {self._log_name} no need to update from repository - set status True (found)")
                    self._file.repo_status = True
            self._file.save()
        else:
            logger.info(f"Folder repository not found for file {self._log_name}")

    def _handle_err(self, err_msg: str, lvl: int = 0) -> None:
        msg = f"File {self._log_name} - {err_msg}" if self._log_name else err_msg
        if lvl == 2:
            logger.critical(msg)
        elif lvl == 1:
            logger.error(msg)
        else:
            logger.warning(msg)
        # raise AssertionError(msg)

    def _save_error_file(self):
        """ Save error file to analyze  """
        err_file_name = f'err_{self._file.id}.txt'
        try:
            err_file_path = settings.STORAGE_ERRORS.save(err_file_name, self._file.data)
            error_file = ErrorFiles(error=self._file.error, data=err_file_path)
            error_file.save()
        except ValidationError:
            self._handle_err('can\'t save error file')
            return False
        logger.info(f'For file {self._log_name} created error file {err_file_name}:{error_file.pk}')
        return error_file.pk


class _ClassUtil:
    """ To shrink main class """

    @staticmethod
    def get_reader(info_obj, copy_path=''):
        """ Get parser for method """
        assert info_obj.method in ['csv', 'html', 'ue', 'row'], "Critical: unknown method to read file"
        assert info_obj.codec, "Critical: codec parameter is required"
        assert isinstance(info_obj.data, str) and info_obj.data, "Critical: data must be type string and not empty"

        reader_params = [info_obj.data, info_obj.codec, info_obj.options, copy_path]
        if info_obj.method == 'csv':
            return LocalizeCSVReader(*reader_params)
        elif info_obj.method == 'html':
            return LocalizeHtmlReader(*reader_params)
        elif info_obj.method == 'ue':
            return LocalizeUEReader(*reader_params)
        elif info_obj.method == 'row':
            return LocalizeRowReader(*reader_params)

    @staticmethod
    def fid_lookup_formula_exist(info: FileScanner) -> bool:
        """ If no formula - don't check by fID when parsing file """
        if info.method == 'row':    # TODO: check this
            return False
        if info.method in ['csv', 'ue']:
            if not info.options['fid_lookup']:
                return False
        return True

    @staticmethod
    def get_lang_short_name(lang_id: int) -> str:
        try:
            return Language.objects.get(id=lang_id).short_name
        except ObjectDoesNotExist:
            return ''
