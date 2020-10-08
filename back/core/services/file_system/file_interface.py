import logging

from django.db.models import Q
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from core.models import Files, ErrorFiles, Translates, Translated
from core.services.file_system.file_cr_trans_copy import CreateTranslatedCopy

from core.services.file_system.file_get_info import DataGetInfo
from core.services.file_system.file_rebuild import FileRebuild
from core.services.git.git_interface import GitInterface

logger = logging.getLogger('logfile')


class LocalizeFileInterface:
    """ Grouped class to manage long time tasks (& others) on file (have subclasses) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.__file = None
        self.error = "File object not set"  # Error don't reset for each function. Get it only when func return False
        try:
            self.__file = Files.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            self.error = f"File not found ID: {file_id}"
            logger.warning(self.error)
        except Exception as exc:
            self.error = f"Unknown exception while getting file object. ID: {file_id} exception: {exc}"
            logger.critical(self.error)
        else:
            self.error = None
            self.__lang_orig = self.__file.lang_orig
            self.__log_name = f'{self.__file.name}(id:{self.__file.id})'

    def parse(self):
        """ Get file info then parse """
        if not self.__check_object('parse'):
            return False
        logger.info(f"Starting parse file ID: {self.__file.id}")
        # Null file object fields
        self.__null_file_fields()
        # Get codec, parse method and check original language texts exist in file
        inf = DataGetInfo(self.__file.data.read(), self.__lang_orig.short_name)
        if inf.info['error']:
            logger.warning(f"File {self.__log_name} get info error: {inf.info['error']}")
            self.error = inf.info['error']
            self.__file.state = 0
            self.__file.error = self.error
            self.__file.save()
            return False
        logger.info(f"File {self.__log_name} get info success")
        self.__file.codec = inf.info['codec']
        self.__file.method = inf.info['method']
        self.__file.options = inf.info['options']
        # Rebuild file
        options = [self.__file.name, self.__file.id, self.__file.lang_orig.id, inf.info['method'], inf.info['options']]
        logger.info('Build marks for file {}(id:{}) language: {} method: {} options: {}'.format(*options))
        file_rebuilding = FileRebuild(self.__file.data.path, inf.info['codec'], *options)
        if file_rebuilding.error:
            logger.warning(f"File {self.__log_name} build marks error: {file_rebuilding.error}")
            self.error = file_rebuilding.error
            self.__file.state = 0
            self.__file.error = self.error
            self.__file.save()
            return False
        logger.info(f"File {self.__log_name} rebuild success")
        self.__file.state = 2
        self.__file.words = file_rebuilding.stats['words']
        self.__file.items = file_rebuilding.stats['items']
        self.__file.save()
        return True

    def create_mark_translate(self, translator_id, mark_id, lang_id, text, md5sum=None, **kwargs):
        """ API FUNC: Create or update translate(s) and return response data with status code """
        # TODO: Log translates
        if not self.__check_object('create_mark_translate'):
            self.error = self.error if self.error else 'unknown'
            pass  # Error must be already set
        elif not mark_id or not lang_id or not translator_id:
            self.error = "Request params error"
        # Can't change original text
        elif lang_id == self.__file.lang_orig.id:
            # TODO: permissions check - mb owner can change ?
            self.error = "Can't change original text"
        # Check lang_translate in list of need translate languages
        elif lang_id not in self.__file.translated_set.values_list("language", flat=True):
            self.error = "No need translate to this language"
        if self.error:
            logger.warning(f"For file {self.__log_name} create translate error: {self.error}")
            return {"err": self.error}, status.HTTP_400_BAD_REQUEST
        # Get or create translate(s)
        if md5sum:  # multi update
            # Check if translates exist with same md5
            translates = Translates.objects.filter(mark__file=self.__file, language=lang_id, mark__md5sum=md5sum)
            control_marks = self.__file.filemarks_set.filter(md5sum=md5sum)
        else:
            translates = Translates.objects.filter(mark__file=self.__file, language=lang_id, mark__id=mark_id)
            control_marks = self.__file.filemarks_set.filter(id=mark_id)
        # TODO: check text language and other
        translates.update(text=text)
        # Add new translates if mark(marks for md5) have no translates
        if translates.count() != control_marks.count():
            def_obj = {"translator_id": translator_id, "language_id": lang_id, "text": text}
            objects = [Translates(**def_obj, mark=mark) for mark in control_marks if
                       mark.id not in translates.values_list("mark", flat=True)]
            Translates.objects.bulk_create(objects)
        # Translate for response
        return_trans = translates.get(mark_id=mark_id)
        return return_trans, status.HTTP_200_OK

    def update_all_language_progress(self):
        """ Update file progress for all languages """
        for lang in self.__file.translated_set.all():
            self.update_language_progress(lang.id)

    def update_language_progress(self, lang_id):
        """ Update file progress for language """
        if not self.__check_object('check_progress'):
            return False
        try:
            progress = self.__file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            logger.critical(f"For file {self.__file.id} related translated object not found: language {lang_id}")
            return False
        translated_items_amount = self.__file.filemarks_set.filter(Q(translates__language=lang_id),
                                                                   ~Q(translates__text__exact="")).count()
        progress.items = translated_items_amount
        progress.save()
        if self.__file.items != translated_items_amount:
            if self.__file.items < translated_items_amount:
                logger.critical(f"For file {self.__log_name} translates items more then file have")
            return False
        return True

    def create_progress(self):
        """ Create related translate progress to file """
        if self.__check_object('create_progress'):
            translate_to_ids = self.__file.folder.project.translate_to.values_list('id', flat=True)
            objects_to_create = [Translated(file_id=self.__file.id, language_id=lang_id) for lang_id in
                                 translate_to_ids]
            Translated.objects.bulk_create(objects_to_create)
            return True
        return False

    def create_translated_copy(self, lang_to_id):
        """ Create translation copy of the file """
        if self.__check_object('create_translated_copy') and self.update_language_progress(lang_to_id):
            tr_copy = CreateTranslatedCopy(self.__file, lang_to_id)
            if tr_copy.copy_name:
                progress = self.__file.translated_set.get(language_id=lang_to_id)
                progress.translate_copy = tr_copy.copy_name
                progress.finished = True
                progress.save()
                return True
        return False

    def update_copy_in_repo(self, lang_id):
        """ Update file translated copy in repository """
        if self.__check_object('update_copy_in_repo') and self.__file.folder.repo_status:
            copy = self.__file.translated_set.get(language_id=lang_id)
            git_manager = GitInterface()
            try:
                git_manager.repo = model_to_dict(self.__file.folder.folderrepo)
                new_file_sha, err = git_manager.upload_file(copy.translate_copy.path, copy.repo_sha)
            except AssertionError as err:
                logger.warning(f"Can't set repository for file {self.__log_name} error: {err}")
                return False
            if err:
                logger.error(f"Error uploading copy for {self.__log_name} to lang {lang_id} - {err}")
                return False
            copy.repo_hash = new_file_sha
            copy.save()
            logger.info(f"Success uploaded file copy {self.__log_name} for lang {lang_id} to repository")
            return True
        else:
            logger.info(f"Folder repository not found for file {self.__log_name}")
        return False

    def update_from_repo(self):
        """ Update file from git repository """
        if self.__check_object('update_from_repo') and self.__file.folder.repo_status:
            self.__file.repo_status = False
            logger.info(f"File {self.__log_name} trying to update from repository - set status False (not found)")
            # Get list of updated files from git
            git_manager = GitInterface()
            try:
                git_manager.repo = model_to_dict(self.__file.folder.folderrepo)
                new_sha, err = git_manager.update_file(self.__file.data.path, self.__file.repo_sha)
            except AssertionError as error:
                logger.error(f"Can't set repository for file {self.__log_name} error: {error}")
            else:
                if err:
                    logger.warning(f"File update from repository error: {err}")
                elif new_sha:
                    logger.info(f"File {self.__log_name} updated from repository - set status True (found)")
                    self.__file.repo_status = True
                    self.__file.repo_sha = new_sha
                else:  # If not set - file not updated in repository
                    logger.info(f"File {self.__log_name} no need to update from repository - set status True (found)")
                    self.__file.repo_status = True
            self.__file.save()
        else:
            logger.info(f"Folder repository not found for file {self.__log_name}")

    def save_error(self):
        """ Save error file to analyze  """
        if not self.error:
            logger.warning("Can't save error file because there are no errors")
            return False
        if not self.__check_object('save_error'):
            return False
        try:
            error_file = ErrorFiles(error=self.error, data=self.__file.data)
            error_file.save()
        except ValidationError:
            logger.error(f"Can't save error file for {self.__log_name} ")
            return False
        logger.info(f'For file {self.__log_name} created error file {error_file.pk}')
        return error_file.pk, self.error

    def __null_file_fields(self):
        """ Refresh database object file """
        if self.__file.state != 1:
            self.__file.words = None
            self.__file.items = None
            self.__file.codec = ''
            self.__file.method = ''
            self.__file.error = ''
            self.__file.options = None

    def __check_object(self, func_name=''):
        if self.__file:
            return True
        logger.error(f'File object not set when call "{func_name}"')
        return False
