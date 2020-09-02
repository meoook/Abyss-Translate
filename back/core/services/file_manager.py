import logging

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from core.models import Files, ErrorFiles, Translates, Translated
from core.services.file_cr_trans_copy import CreateTranslatedCopy

from core.services.file_get_info import DataGetInfo
from core.services.file_rebuild import FileRebuild
from core.services.git_manager import GitManage

logger = logging.getLogger('django')


class LocalizeFileManager:
    """ Grouped class to manage long time tasks on file (have subclasses) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.__file = None
        self.error = True
        try:
            self.__file = Files.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            self.error = f"File not found ID: {file_id}"
            logger.warning(self.error)
        except Exception as exc:
            self.error = f"Unknown exception while getting file object. ID: {file_id} exception: {exc}"
            logger.critical(self.error)
        else:
            self.error = False
            self.__lang_orig = self.__file.lang_orig
            self.__log_name = f'{self.__file.name}(id:{self.__file.id})'

    def parse(self):
        """ Get file info then parse """
        if not self.__file:
            logger.error(f"File object parse error: {self.error if self.error else 'unknown'}")
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
        """ Create or update translates. Update translate progress. If finished - create translate file. """
        # TODO: Log translates
        if not self.__file:
            self.error = self.error if self.error else 'unknown'    # Error must be already set
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
            objs = [Translates(**def_obj, mark=mark) for mark in control_marks if mark.id not in translates.values_list("mark", flat=True)]
            Translates.objects.bulk_create(objs)
        # Translate for response
        return_trans = translates.get(mark_id=mark_id)
        return return_trans, status.HTTP_200_OK

    def check_progress(self, lang_id):
        """ Update file progress for language """
        if not self.__file:
            logger.error(f"File object check progress error: {self.error if self.error else 'unknown'}")
            return False
        try:
            progress = self.__file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:    # App error, must be fixed
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
        if not self.__file:
            logger.error(f"File object create progress error: {self.error if self.error else 'unknown'}")
            return False
        translate_to_ids = self.__file.folder.project.translate_to.values_list('id', flat=True)
        objects_to_create = [Translated(file_id=self.__file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objects_to_create)

    def create_translated_copy(self, lang_to_id):
        """ Create translation copy of the file """
        if not self.__file:
            logger.error(f"File object check progress error: {self.error if self.error else 'unknown'}")
        elif self.check_progress(lang_to_id):   # Progress exist and finished
            tr_copy = CreateTranslatedCopy(self.__file, lang_to_id)
            if tr_copy.copy_name:
                progress = self.__file.translated_set.get(language_id=lang_to_id)
                progress.translate_copy = tr_copy.copy_name
                progress.finished = True
                progress.save()
                return True
        return False

    def update_from_repo(self):
        """ Update file from repo (then parse?) """
        if not self.__file:
            logger.error(f"File object update from repo error: {self.error if self.error else 'unknown'}")
        elif self.__file.folder.repo_status:
            logger.info(f"File {self.__log_name} updating from repo")
            f = self.__file
            one_file_list = ({'id': f.id, 'name': f.name, 'hash': f.repo_hash, 'path': f.data.path},)
            # Get list of updated files from git
            git_manager = GitManage()
            git_manager.repo = self.__file.folder.folderrepo
            updated_files = git_manager.update_files(one_file_list)
            return len(updated_files) == 1
        return False

    def __null_file_fields(self):
        """ Refresh database object file """
        if self.__file.state != 1:
            self.__file.words = None
            self.__file.items = None
            self.__file.codec = ''
            self.__file.method = ''
            self.__file.error = ''
            self.__file.options = None

    def save_error(self):
        """ Save error file to analyze  """
        if not self.error:
            logger.warning("Can't save error file because there are no errors")
            return False
        if not self.__file:
            logger.error(f"File object not set to save error: {self.error if self.error else 'unknown'}")
            return False
        try:
            error_file = ErrorFiles(error=self.error, data=self.__file.data)
            err_obj = error_file.save()
        except ValidationError:
            logger.error(f"Can't save error file for {self.__log_name} ")
            return False
        logger.info(f'For file {self.__log_name} created error file {err_obj.id}')
        return err_obj.id, self.error
