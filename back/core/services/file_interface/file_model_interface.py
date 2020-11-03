import logging

from django.db.models import Q
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from core.models import File, ErrorFiles, Translate, Translated, TranslateChangeLog, MarkItem, FileMark

from core.services.file_interface.file_find_item import FileItemsFinder
from core.services.file_interface.file_model_basic import FileModelBasicApi
from core.services.file_interface.file_scanner import FileScanner
from core.services.file_system.file_cr_trans_copy import CreateTranslatedCopy

from core.services.file_system.file_get_info import DataGetInfo
from core.services.file_system.file_rebuild import FileRebuild
from core.services.git.git_interface import GitInterface

logger = logging.getLogger('logfile')


class FileModelAPI(FileModelBasicApi):
    """ DB API to work with file object (file created in view when uploaded) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        super().__init__(file_id)
        # Object flags and params
        self.__structure_changed = False  # Flag to check if file structure have changed
        self.__fid_lookup_changed = False  # Flag to check if file fID formula changed
        self.__fid_lookup_exist = self.__fid_lookup_formula_exist

    @property
    def __fid_lookup_formula_exist(self):
        """ If no formula - don't check by fID when parsing file """
        if self._file.method in ['csv', 'ue']:
            if not self._file.options['fid_lookup']:
                return False
        return True

    def __refresh_file(self):
        """ When new(updated) file in IO -> Return true - if no errors while getting info """
        info = FileScanner(self._file.data.path, self._lang_orig.short_name)
        if info.error:
            self._handle_err("File {} get info error:" + info.error)
            self._file.state = 0
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
                self.__build_file_translates(info, self._lang_orig.id)
            except AssertionError as err:
                self._handle_err("File {} build marks error: " + str(err))
                self._file.state = 0
                self._file.error = err
                self._file.save()
                return False
            logger.info(f"File {self._log_name} rebuild success")
            return True

    def __load_translates_from_copy(self, copy_path, lang_id):
        """ Add new translates to existing mark items for selected language """
        info = FileScanner(copy_path, lang_id)
        if not info.error:
            self.__build_file_translates(info_obj=info, lang_id=lang_id)

    def __build_file_translates(self, info_obj, lang_id):
        """ Update, delete, insert translates while parsing file for selected language """
        is_original = self._lang_orig.id == lang_id
        reader = self._get_reader(info_obj)
        finder = FileItemsFinder(self._file.id, self.__fid_lookup_exist, is_original)

        for file_mark in reader:
            if self.__fid_lookup_exist:
                if finder.find_by_fid(file_mark['fid']):
                    for item in file_mark['items']:
                        self._tr_change_by_parser(file_mark['fid'], item['item_number'], lang_id, item['text'])
                    continue
            if is_original:
                mark = FileMark(
                    file_id=self._file.id,
                    fid=file_mark['fid'],
                    words=file_mark['words'],
                    search_words=file_mark['search_words'],
                    context=file_mark['context'],
                )
                mark.save()
                for mark_item in file_mark['items']:
                    item_obj = MarkItem(**mark_item, mark=mark)
                    item_obj.save()
                    # Prepare translates
                    translates_with_text = finder.find_by_md5(mark_item['md5sum'])
                    # Crate translate and empty translates for other language
                    translates_to_create = []
                    for lang_to_tr in self._file.folder.project.translate_to.values_list('id', flat=True):
                        if lang_to_tr == lang_id:
                            self._tr_create_by_parser(item_obj.pk, lang_to_tr, mark_item['text'], mark_item['warning'])
                        elif lang_to_tr in translates_with_text.keys():
                            self._tr_create_by_parser(
                                item_id=item_obj.pk,
                                lang_id=lang_to_tr,
                                text=translates_with_text[lang_to_tr]['text'],
                                warning=f"Translate taken from id:{translates_with_text[lang_to_tr]['item_id']}"
                            )
                        else:
                            self._tr_create_by_parser(item_obj.pk, lang_to_tr, '', '')
                else:
                    self._handle_err("Can't fill translates without fID formula - {}")
        if is_original:
            # Save results
            self._file.state = 2
            self._file.items, self._file.words = reader.stats
            self._file.save()
            self._file.markitem_set.filter(fid__in=[finder.unused_fid]).delete()  # Delete unused marks
        self._file_progress_refresh_all()   # Refresh translates progress after adding new objects

    # def create_mark_translate(self, translator_id, mark_id, lang_id, text, md5sum=None, **kwargs):
    #     """ API FUNC: Create or update translate(s) and return response data with status code """
    #     # TODO: Log translates
    #     if not self.__check_object('create_mark_translate'):
    #         self.error = self.error if self.error else 'unknown'
    #         pass  # Error must be already set
    #     elif not mark_id or not lang_id or not translator_id:
    #         self.error = "Request params error"
    #     # Can't change original text
    #     elif lang_id == self.__file.lang_orig.id:
    #         # TODO: permissions check - mb owner can change ?
    #         self.error = "Can't change original text"
    #     # Check lang_translate in list of need translate languages
    #     elif lang_id not in self.__file.translated_set.values_list("language", flat=True):
    #         self.error = "No need translate to this language"
    #     if self.error:
    #         logger.warning(f"For file {self.__log_name} create translate error: {self.error}")
    #         return {"err": self.error}, status.HTTP_400_BAD_REQUEST
    #     # Get or create translate(s)
    #     if md5sum:  # multi update
    #         # Check if translates exist with same md5
    #         translates = Translate.objects.filter(mark__file=self.__file, language=lang_id, mark__md5sum=md5sum)
    #         control_marks = self.__file.filemarks_set.filter(md5sum=md5sum)
    #     else:
    #         translates = Translate.objects.filter(mark__file=self.__file, language=lang_id, mark__id=mark_id)
    #         control_marks = self.__file.filemarks_set.filter(id=mark_id)
    #     # TODO: check text language and other
    #     translates.update(text=text)
    #     # Add new translates if mark(marks for md5) have no translates
    #     if translates.count() != control_marks.count():
    #         def_obj = {"translator_id": translator_id, "language_id": lang_id, "text": text}
    #         objects = [Translate(**def_obj, mark=mark) for mark in control_marks if
    #                    mark.id not in translates.values_list("mark", flat=True)]
    #         Translate.objects.bulk_create(objects)
    #     # Log translate change
    #     log_objects = [TranslateChangeLog(user_id=translator_id, translate_id=x.id, text=text) for x in translates]
    #     TranslateChangeLog.objects.bulk_create(log_objects)
    #     # Translate for response
    #     return_trans = translates.get(mark_id=mark_id)
    #     return return_trans, status.HTTP_200_OK
    #
    # def create_translated_copy(self, lang_to_id):
    #     """ Create translation copy of the file """
    #     if self.__check_object('create_translated_copy') and self.update_language_progress(lang_to_id):
    #         tr_copy = CreateTranslatedCopy(self.__file, lang_to_id)
    #         if tr_copy.copy_name:
    #             progress = self.__file.translated_set.get(language_id=lang_to_id)
    #             progress.translate_copy = tr_copy.copy_name
    #             progress.finished = True
    #             progress.save()
    #             return True
    #     return False
    #
    # def update_copy_in_repo(self, lang_id):
    #     """ Update file translated copy in repository """
    #     if self.__check_object('update_copy_in_repo') and self.__file.folder.repo_status:
    #         copy = self.__file.translated_set.get(language_id=lang_id)
    #         git_manager = GitInterface()
    #         try:
    #             git_manager.repo = model_to_dict(self.__file.folder.folderrepo)
    #             new_file_sha, err = git_manager.upload_file(copy.translate_copy.path, copy.repo_sha)
    #         except AssertionError as err:
    #             logger.warning(f"Can't set repository for file {self.__log_name} error: {err}")
    #             return False
    #         if err:
    #             logger.error(f"Error uploading copy for {self.__log_name} to lang {lang_id} - {err}")
    #             return False
    #         copy.repo_hash = new_file_sha
    #         copy.save()
    #         logger.info(f"Success uploaded file copy {self.__log_name} for lang {lang_id} to repository")
    #         return True
    #     else:
    #         logger.info(f"Folder repository not found for file {self.__log_name}")
    #     return False
    #
    # def update_from_repo(self):
    #     """ Update file from git repository """
    #     if self.__check_object('update_from_repo') and self.__file.folder.repo_status:
    #         self.__file.repo_status = False
    #         logger.info(f"File {self.__log_name} trying to update from repository - set status False (not found)")
    #         # Get list of updated files from git
    #         git_manager = GitInterface()
    #         try:
    #             git_manager.repo = model_to_dict(self.__file.folder.folderrepo)
    #             new_sha, err = git_manager.update_file(self.__file.data.path, self.__file.repo_sha)
    #         except AssertionError as error:
    #             logger.error(f"Can't set repository for file {self.__log_name} error: {error}")
    #         else:
    #             if err:
    #                 logger.warning(f"File update from repository error: {err}")
    #             elif new_sha:
    #                 logger.info(f"File {self.__log_name} updated from repository - set status True (found)")
    #                 self.__file.repo_status = True
    #                 self.__file.repo_sha = new_sha
    #             else:  # If not set - file not updated in repository
    #                 logger.info(f"File {self.__log_name} no need to update from repository - set status True (found)")
    #                 self.__file.repo_status = True
    #         self.__file.save()
    #     else:
    #         logger.info(f"Folder repository not found for file {self.__log_name}")
    #
    # def save_error(self):
    #     """ Save error file to analyze  """
    #     if not self.error:
    #         logger.warning("Can't save error file because there are no errors")
    #         return False
    #     if not self.__check_object('save_error'):
    #         return False
    #     try:
    #         error_file = ErrorFiles(error=self.error, data=self.__file.data)
    #         error_file.save()
    #     except ValidationError:
    #         logger.error(f"Can't save error file for {self.__log_name} ")
    #         return False
    #     logger.info(f'For file {self.__log_name} created error file {error_file.pk}')
    #     return error_file.pk, self.error

