import logging

from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from rest_framework import status

from core.models import ErrorFiles, Translate, TranslateChangeLog

from core.services.file_interface.file_model_basic import FileModelBasicApi
from core.services.file_interface.file_scanner import FileScanner

from core.services.git.git_interface import GitInterface

logger = logging.getLogger('django')


class FileModelAPI(FileModelBasicApi):
    """ File API to work with file object in application (os and model) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        super().__init__(file_id)
        # Object flags and params
        self.__structure_changed = False   # Flag to check if file structure have changed  FIXME - not used
        self.__fid_lookup_changed = False  # Flag to check if file fID formula changed

    def file_new(self):
        """ When new file -> update from repo -> get info -> parse -> cr progress """
        try:
            self.__update_from_repo()
            if self.__refresh_file():
                self._file_progress_create()
            else:
                self._save_error()
        except AssertionError:
            logger.warning('Error loading file xxx')

    def file_refresh(self, lang_id, tmp_data):  # TODO: Optimize - no need to save! data in file for translated copy
        is_original = lang_id == self._lang_orig.id
        print(lang_id, type(lang_id), self._lang_orig.id, type(self._lang_orig.id), lang_id == self._lang_orig.id)
        if is_original:  # Replace original file
            # FIXME - if file linked with repo - disable upload
            self._file.data = tmp_data
            self._file.save()
            self.__refresh_file()  # Run rebuild
            self._file_progress_up_or_cr()  # Create(if no 'translated_set') or update file progress
        else:  # Write new file to disk
            # If file left in error storage - it's an error :) -> copy deleted after finish
            tmp_file = settings.STORAGE_ERRORS.save(f'{self._file.id}_{lang_id}.txt', tmp_data)
            self.__load_translates_from_copy(lang_id, tmp_file)  # Run rebuild language translates
            settings.STORAGE_ERRORS.delete(tmp_file)
            self._file_progress_refresh(lang_id)

    def __refresh_file(self):
        """ Rebuild translates for original language """
        info = FileScanner(self._file.data.path, self._lang_orig.short_name)
        if info.error:
            self._handle_err("File {} get info error:" + info.error)
            self._file.error = info.error
            self._file.save()
            return False
        else:
            logger.info(f"File {self._log_name} get info success - method:{info.method} options:{info.options}")
            self._file.codec = info.codec
            self._file.method = info.method
            self._file.options = info.options
            # Rebuild file
            logger.info(f'Build marks for file {self._log_name}')
            try:
                self._file_build_translates(info, self._lang_orig.id)
            except AssertionError as err:
                self._handle_err("File {} build marks error: " + str(err))
                self._file.error = err
                self._file.save()
                return False
            return True

    def __load_translates_from_copy(self, copy_path, lang_id):  # FIXME: use data for copy - no need to save file
        """ Add new translates from user upload """
        info = FileScanner(copy_path, lang_id)
        if not info.error:
            self._file_build_translates(info_obj=info, lang_id=lang_id)
        else:
            print(info.error)
            self._handle_err("Error while getting translate copy for file {}")

    def create_translated_copy(self, lang_to_id):
        """ Create translation copy of the file """
        info = FileScanner(self._file.data.path)
        copy_path = ''  # TODO: copy path creator
        reader = self._get_reader(info, copy_path)

        # TODO - get all translates and find from there when parse (pre-done)
        tr_items = {}
        for translate_item in Translate.objects.filter(item__mark__file__id=self._file.id, language_id=lang_to_id) \
                .values('item__mark__fid', 'item__item_number', 'text'):
            if translate_item['item__mark__file_id'] in tr_items.keys():
                translate_item['item__mark__file_id'] \
                    .append({'item_number': translate_item['item__item_number'], 'text': translate_item['text']})
            else:
                translate_item['item__mark__file_id'] = [
                    {'item_number': translate_item['item__item_number'], 'text': translate_item['text']}, ]

        for file_mark in reader:
            if file_mark['fid'] in tr_items:
                reader.change_item_content_and_save(file_mark['fid'])
        reader.change_item_content_and_save([{'item_number': 0, 'text': ''}])  # To save - left/unsaved data
        # Update model as finished
        progress = self._file.translated_set.get(language_id=lang_to_id)
        progress.translate_copy = copy_path
        progress.finished = True  # TODO: remove it - because copy can be created not finished
        progress.save()
        return True

    def create_mark_translate(self, translator_id, mark_id, lang_id, text, md5sum=None, **kwargs):
        """ API FUNC: Create or update translate(s) and return response data with status code """
        # TODO: Log translates
        # == Error checks ==
        error = None
        if not mark_id or not lang_id or not translator_id:
            self._handle_err("Request params error")
            error = "request params error"
        # Can't change original text
        elif lang_id == self._file.lang_orig.id:
            # TODO: permissions check - mb owner can change ?
            error = "can't change original text"
        # Check lang_translate in list of need translate languages
        elif lang_id not in self._file.translated_set.values_list("language", flat=True):
            error = "no need translate to this language"
        if error:
            self._handle_err("For file {} create translate error: " + error)
            return {"err": error}, status.HTTP_400_BAD_REQUEST
        # == Get or create translate(s) ==
        if md5sum:  # multi update
            # Check if translates exist with same md5
            translates = Translate.objects.filter(item__mark__file=self._file, language=lang_id,
                                                  item__mark__md5sum=md5sum)
            control_marks = self._file.filemarks_set.filter(md5sum=md5sum)
        else:
            translates = Translate.objects.filter(item__mark__file=self._file, language=lang_id, item__mark__id=mark_id)
            control_marks = self._file.filemarks_set.filter(id=mark_id)
        # TODO: check text language and other
        translates.update(text=text)
        # Add new translates if mark(marks for md5) have no translates
        if translates.count() != control_marks.count():
            def_obj = {"translator_id": translator_id, "language_id": lang_id, "text": text}
            objects = [Translate(**def_obj, mark=mark) for mark in control_marks if
                       mark.id not in translates.values_list("mark", flat=True)]
            Translate.objects.bulk_create(objects)
        # Log translate change
        log_objects = [TranslateChangeLog(user_id=translator_id, translate_id=x.id, text=text) for x in translates]
        TranslateChangeLog.objects.bulk_create(log_objects)
        # Translate for response
        return_trans = translates.get(mark_id=mark_id)
        return return_trans, status.HTTP_200_OK

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
