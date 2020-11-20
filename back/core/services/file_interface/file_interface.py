import logging

from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import status

from core.models import Translate

from core.services.file_interface.file_model_basic import FileModelBasicApi
from core.services.file_interface.file_scanner import FileScanner

from core.services.git.git_interface import GitInterface

logger = logging.getLogger('django')


class FileModelAPI(FileModelBasicApi):
    """ File API to work with file object in application (os and model) """

    def __init__(self, file_id: int):
        """ Get file object from database to do other actions """
        super().__init__(file_id)

    def file_new(self, original_lang_id: int, file_path: str):
        """ When new file -> update from repo -> get info -> parse -> cr progress """
        try:
            self.__update_from_repo()
            if not self.file_refresh(file_path, original_lang_id, True):
                self._save_error()
        except AssertionError:
            logger.warning(f'Error loading file {file_path}')

    def file_refresh(self, tmp_path: str, lang_id: int, is_original=False):
        """ File refresh translates (mark-item-translate) for selected language """
        current_options = self._file.options
        info = FileScanner(tmp_path, self._get_lang_short_name(lang_id))
        """ Phase 0: Delete progress for new original (then refresh if no errors) """
        if is_original:
            self._file.translated_set.all().delete()
        """ Phase 1: Check info for critical errors """
        if info.error:
            if is_original:
                self._handle_err(f"get info error:{info.error}")
                self._file.error = info.error
                # TODO: we need to delete old fID
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
            languages = self._file_progress_create()
            try:
                logger.info(f'File {self._log_name} try build marks as original')
                self._file_rebuild_original(lang_id, languages, info)  # file.save() called if success
            except AssertionError as err:
                self._handle_err("File {} build marks error: " + str(err))
                self._file.error = err
                self._file.save()
                return False
            else:
                """ Phase 5: Refresh progress """
                self._file_progress_refresh_all()
        else:
            logger.info(f'File {self._log_name} try build marks for language {lang_id}')
            try:
                self._file_rebuild_translates(lang_id, info)
            except AssertionError as err:
                self._handle_err("File {} build translates error: " + str(err))
            finally:
                """ Phase 5: Refresh progress and del tmp data """
                settings.STORAGE_ERRORS.delete(tmp_path)
                self._file_progress_refresh(lang_id)
        return True

    def create_translated_copy(self, lang_to_id: int):
        """ Create translation copy of the file """
        original_file_path = self._file.data.path
        info = FileScanner(path=original_file_path)
        copy_path = self._get_translate_copy_path(original_file_path, self._get_lang_short_name(lang_to_id))
        reader = self._get_reader(info_obj=info, copy_path=copy_path)

        tr_items = {}
        for translate_item in Translate.objects.filter(item__mark__file__id=self._file.id, language_id=lang_to_id) \
                .values('item__mark__fid', 'item__item_number', 'text'):
            _item = {'item_number': translate_item['item__item_number'], 'text': translate_item['text']}
            if translate_item['item__mark__fid'] in tr_items.keys():
                tr_items['item__mark__fid'].append(_item)
            else:
                tr_items['item__mark__fid'] = [_item, ]

        for file_mark in reader:
            if file_mark['fid'] in tr_items:
                reader.change_item_content_and_save(file_mark['fid'])
        reader.change_item_content_and_save([{'item_number': 0, 'text': ''}])  # To save - left/unsaved data
        # Update model as finished
        progress = self._file.translated_set.get(language_id=lang_to_id)
        progress.translate_copy = copy_path
        progress.refreshed = False
        progress.save()

    def translate_change_by_user(self, translator_id, trans_id, text, md5sum=None, **kwargs):
        """ API FUNC: Create or update translate(s) and return response data with status code """
        if not trans_id or not translator_id:
            self._handle_err("request params error")
            return {'err': 'request params error'}, status.HTTP_400_BAD_REQUEST
        try:
            translate = Translate.objects.get(id=trans_id)
        except ObjectDoesNotExist:
            return {'err': 'translate not found'}, status.HTTP_404_NOT_FOUND
        # Can't change original text
        translate_lang_id = translate.language.id
        if translate_lang_id == self._file.lang_orig.id:
            # TODO: permissions check - mb owner can change ?
            return {'err': 'can\'t change original text'}, status.HTTP_400_BAD_REQUEST
        if md5sum:  # multi update
            filter_options = {'item__mark__file': self._file, 'language': translate_lang_id, 'item__md5sum': md5sum}
            for translate_obj in Translate.objects.filter(**filter_options):
                self._tr_change_by_user(translate_obj, text, user_id=translator_id)
        else:
            self._tr_change_by_user(translate, text, user_id=translator_id)
        self._file_progress_refresh(translate_lang_id)
        return translate, status.HTTP_201_CREATED

    def update_copy_in_repo(self, lang_id):
        """ Update file translated copy in repository """
        if self._file.folder.repo_status:
            copy = self._file.translated_set.get(language_id=lang_id)
            git_manager = GitInterface()
            try:
                git_manager.repo = model_to_dict(self._file.folder.folderrepo)
                new_file_sha, err = git_manager.upload_file(copy.translate_copy.path, copy.repo_sha)
            except AssertionError as err:
                logger.warning(f"Can't set repository for file {self._log_name} error: {err}")
                return False
            if err:
                logger.error(f"Error uploading copy for {self._log_name} to lang {lang_id} - {err}")
                return False
            copy.repo_hash = new_file_sha
            copy.save()
            logger.info(f"Success uploaded file copy {self._log_name} for lang {lang_id} to repository")
            return True
        else:
            logger.info(f"Folder repository not found for file {self._log_name}")
        return False

    def __update_from_repo(self):
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
                logger.error(f"Can't set repository for file {self._log_name} error: {error}")
            else:
                if err:
                    logger.warning(f"File update from repository error: {err}")
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
