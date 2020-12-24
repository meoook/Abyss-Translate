import logging

from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from core.services.git_interface.git_interface import GitInterface
from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.file_related_model import FileRelatedModelApi
from core.services.file_interface.file_find_item import FileItemsFinder
from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_row import LocalizeRowReader
from core.services.file_interface.file_read_ue import LocalizeUEReader
from core.services.file_interface.file_scanner import FileScanner

from core.models import Translate, File, Translated, MarkItem, ErrorFiles, Language

logger = logging.getLogger('django')


class FileModelApi:
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
            self._log_err(f"File not found ID: {file_id}")
        except Exception as exc:
            self._log_err(f"Unknown exception while getting file object. ID: {file_id} exception: {exc}", 2)
        else:
            # Object flags and params
            # self._lang_orig = self._file.lang_orig
            self._log_name = f'{self._file.name}(id:{self._file.id})'
            self._structure_changed = False   # Flag to check if file structure have changed

    def _file_refresh(self, tmp_path: str, lang_id: int, is_original: bool) -> bool:
        """ File refresh translates (mark-item-translate) for selected language """
        _current_options: dict[str, any] = self._file.options
        _lang_short_name: str = _ClassUtil.get_lang_short_name(lang_id)
        _info = FileScanner(tmp_path, _lang_short_name)
        """ Phase 0: Delete progress for new original (then refresh if no errors) """
        if is_original:
            self._file.translated_set.all().delete()
        """ Phase 1: Check info for critical errors """
        if _info.error:
            if is_original:
                self._log_err(f"get info error:{_info.error}")
                self._file.error = _info.error
                self._file.save()
            else:
                self._log_err(f"uploaded {tmp_path} file get info error:{_info.error}")
                settings.STORAGE_ERRORS.delete(tmp_path)
            return False
        """ Phase 2: Check file if structure change (new = true) """
        if _current_options != _info.options:
            self._log(f'loaded file {tmp_path} structure not same as original')
            if is_original:
                self._structure_changed = True
            else:
                self._log_err("can't fill translates if structure not same")
                settings.STORAGE_ERRORS.delete(tmp_path)
                return False
        """ Phase 3: Update structure if upload file is original language """
        self._log(f'get info success - method:{_info.method}')
        if is_original and self._structure_changed:
            self._log(f'uploaded new original with changed structure:{_info.options}')
            self._file.codec = _info.codec
            self._file.method = _info.method
            self._file.options = _info.options
        """ Phase 4: Rebuild file """
        if is_original:
            languages = self.__file_progress_create()
            try:
                self._log('try build marks as original')
                self.__file_rebuild_original(lang_id, languages, _info)  # file.save() called if success
            except AssertionError as err:
                self._log_err(f"build marks error:{err}")
                self._file.error = err
                self._file.save()
                return False
            else:
                """ Phase 5: Refresh progress """
                self.__file_progress_refresh_all()
        else:
            self._log(f'try build marks for language:{lang_id}')
            try:
                self.__file_rebuild_translates(lang_id, _info)
            except AssertionError as err:
                self._log_err(f"build translates error:{err}")
            finally:
                """ Phase 5: Refresh progress and del tmp data """
                settings.STORAGE_ERRORS.delete(tmp_path)
                self._file_progress_refresh(lang_id)
        return True

    def __file_rebuild_original(self, orig_id: int, languages_to: list[int], info_obj: FileScanner) -> None:
        """ Update, delete, insert translates while parsing file -> then refresh file stats """
        if not _ClassUtil.fid_lookup_formula_exist(info_obj):
            self._log('don\'t have fID formula and will build by index')

        _reader = _ClassUtil.get_reader(info_obj)
        _finder = FileItemsFinder(self._file.id)  # Prepare finder and remember old marks
        for file_mark in _reader:
            _model_api = FileRelatedModelApi(orig_id, languages_to)  # Api to work with models
            # Getting FileMark object
            _mark = _model_api.mark_create_or_update(self._file.id, file_mark)
            # Add mark id not to delete
            _finder.used_mark_id = _mark.pk
            # After adding MarkItems - delete old unused (item number not in list)
            _numbers_not_to_delete: list[int] = []
            for mark_item in file_mark['items']:
                _numbers_not_to_delete.append(mark_item['item_number'])
                # Prepare translates to find by inner text (old translates in DB)
                _translates_with_text = _finder.find_by_md5(mark_item['md5sum'])
                # Create or update MarkItem and it's Translates
                _model_api.item_refresh(_mark.pk, mark_item, _translates_with_text)
            # Delete old MarkItems for Mark
            _delete_amount, _ = _mark.markitem_set.exclude(item_number__in=_numbers_not_to_delete).delete()
            if _delete_amount and not self._structure_changed:  # Can not be new items if structure don't change
                self._log_err(f'structure not changed but was {_delete_amount} items to delete', 2)
        # Delete unused Marks
        _amount, _ = self._file.filemark_set.exclude(id__in=_finder.used_mark_id).delete()
        self._log(f'delete {_amount} unused marks')
        # Save results
        self._file.error = ''
        self._file.items, self._file.words = _reader.stats
        self._file.save()
        self._log('build as original success')

    def __file_rebuild_translates(self, lang_id, info_obj) -> None:
        """ Update, delete, insert translates while parsing file for selected language then update progress """
        if _ClassUtil.fid_lookup_formula_exist(info_obj):
            warning = ''
        else:
            warning = 'translate placed by file index'  # TODO: It ok to change translate without formula ?
            self._log_err('translate copy don\'t have fID formula and will build by index')

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
                        self._log_err(f"can't find translate for fID:{file_mark['fid']} to fill language:{lang_id}")
        self._log('build as copy success')

    def _file_progress_refresh(self, lang_id) -> bool:
        """ Refresh file progress for language """
        try:
            progress = self._file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            self._log_err(f'related translated object not found for language:{lang_id}', 2)
            return False
        translated_items_amount = MarkItem.objects.filter(mark__file_id=self._file.id) \
            .filter(Q(translate__language=lang_id), ~Q(translate__text__exact="")).count()
        progress.items = translated_items_amount
        progress.need_refresh = True   # When progress need_refresh - mark to create new translated copy
        progress.save()
        self._log(f'progress refresh for language:{lang_id}')
        if self._file.items != translated_items_amount:
            if self._file.items < translated_items_amount:
                self._log_err(f"translates items:{translated_items_amount} more then file have", 2)
            return False
        return True

    def __file_progress_refresh_all(self) -> None:
        """ Refresh file progress for all languages """
        for translated in self._file.translated_set.all():
            self._file_progress_refresh(translated.language)

    def __file_progress_create(self) -> list[int]:
        """ Create progress for 'new' file """
        self._log('creating progress for all languages')
        _translate_to_ids = [int(x) for x in self._file.folder.project.translate_to.values_list('id', flat=True)]
        _objects_to_create = [Translated(file_id=self._file.id, language_id=lang_id) for lang_id in _translate_to_ids]
        Translated.objects.bulk_create(_objects_to_create)
        return _translate_to_ids

    def _translate_copy_create(self, lang_id: int) -> None:
        """ Create translation copy of the file to selected language """
        self._log(f'creating translate copy for language:{lang_id}')
        _original_file_path: str = self._file.data.path
        _info = FileScanner(path=_original_file_path)  # Fixme - get info from db_model
        _lang_short_name: str = _ClassUtil.get_lang_short_name(lang_id)
        _copy_path: str = CopyContextControl.get_path(_original_file_path, _lang_short_name)

        _reader = _ClassUtil.get_reader(info_obj=_info, copy_path=_copy_path)

        for file_mark in _reader:
            _mark_translates = Translate.objects\
                .filter(item__mark__file__id=self._file.id, language_id=lang_id, item__mark__fid=file_mark['fid'])\
                .exclude(text__exact="").values('item__item_number', 'text')
            # Remap items as {item_number: xx, text: yy}
            _mark_translates = [{'item_number': tr['item__item_number'], 'text': tr['text']} for tr in _mark_translates]
            # if file_mark['fid'] in tr_items:
            _reader.copy_write_mark_items(_mark_translates)
        # Update model as finished
        _progress = self._file.translated_set.get(language_id=lang_id)
        _progress.translate_copy = _copy_path
        _progress.need_refresh = False   # Set status - copy refreshed
        _progress.save()
        self._log(f'successfully created translate copy for language:{lang_id}')

    def _translate_copy_upload_in_repo(self, lang_id: int) -> bool:
        """ Update file translated copy in repository """
        # TODO: Make choices how to save copy in repo (EN/filename.txt or filename-en.txt)
        self._log(f'try uploading translate copy to repository for language:{lang_id}')
        if self._file.folder.repo_status:
            _copy = self._file.translated_set.get(language_id=lang_id)
            _git_manager = GitInterface()
            try:
                _git_manager.repo = model_to_dict(self._file.folder.folderrepo)
                _new_file_sha, _err = _git_manager.upload_file(_copy.translate_copy.path, _copy.repo_sha)
            except AssertionError as _err:
                self._log_err(f"can't set repository: {_err}")
                return False
            if _err:
                self._log_err(f"error uploading copy to lang {lang_id} - {_err}")
                return False
            _copy.repo_hash = _new_file_sha
            _copy.save()
            self._log(f'successfully uploaded translate copy for language {lang_id}')
            return True
        else:
            self._log('folder repository not set')
        return False

    def _file_download_from_repo(self):
        """ Download file from git repository (replace original) """
        if self._file.folder.repo_status:
            self._file.repo_status = False
            self._log('try to update from repository - set status False (not found)')
            # Get list of updated files from git
            _git_manager = GitInterface()
            try:
                _git_manager.repo = model_to_dict(self._file.folder.folderrepo)
                _new_sha, _err = _git_manager.update_file(self._file.data.path, self._file.repo_sha)
            except AssertionError as error:
                self._log_err(f"can't set repository error: {error}", 1)
            else:
                if _err:
                    self._log_err(f'update from repository error: {_err}')
                elif _new_sha:
                    self._log('updated from repository - set status True (found)')
                    self._file.repo_status = True
                    self._file.repo_sha = _new_sha
                else:  # If not set - file not updated in repository
                    self._log('no need to update from repository - set status True (found)')
                    self._file.repo_status = True
            self._file.save()
        else:
            self._log('folder repository not set')

    def _log_err(self, err_msg: str, lvl: int = 0) -> None:
        """ Log error messages """
        _msg = f"File {self._log_name} - {err_msg}" if self._log_name else err_msg
        if lvl == 2:
            logger.critical(_msg)
        elif lvl == 1:
            logger.error(_msg)
        else:
            logger.warning(_msg)

    def _log(self, msg: str) -> None:
        _msg = f"File {self._log_name} - {msg}" if self._log_name else msg
        logger.info(_msg)

    def _save_error_file(self):
        """ Save error file to analyze  """
        err_file_name = f'err_{self._file.id}.txt'
        try:
            err_file_path = settings.STORAGE_ERRORS.save(err_file_name, self._file.data)
            error_file = ErrorFiles(error=self._file.error, data=err_file_path)
            error_file.save()
        except ValidationError:
            self._log_err('can\'t save error file')
            return False
        self._log(f'created error file {err_file_name}:{error_file.pk}')
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
