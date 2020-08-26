import logging

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from core.models import Files, ErrorFiles, FileMarks, Translates, Translated

from core.services.file_get_info import DataGetInfo
from core.services.file_rebuild import FileRebuild

logger = logging.getLogger('django')


class LocalizeFileManager:
    """ Grouped class to manage long time tasks on file (have subclasses) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.__work_file = None
        self.error = True
        try:
            self.__work_file = Files.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            self.error = f"File not found ID: {file_id}"
            logger.warning(self.error)
        except Exception as exc:
            self.error = f"Unknown exception while getting file object. ID: {file_id} exception: {exc}"
            logger.critical(self.error)
        else:
            self.error = False
            self.__lang_orig = self.__work_file.lang_orig
            self.__log_name = f'{self.__work_file.name}(id:{self.__work_file.id})'

    def parse(self):
        """ Get file info then parse """
        if not self.__work_file:
            logger.error(f"File object parse error: {self.error if self.error else 'unknown'}")
            return False
        logger.info(f"Starting parse file ID: {self.__work_file.id}")
        # Null file object fields
        self.__null_file_fields()
        # Get codec, parse method and check original language texts exist in file
        info = DataGetInfo(self.__work_file.data.read(), self.__lang_orig.short_name)
        if info.info['error']:
            logger.warning(f"File {self.__log_name} get info error: {info.info['error']}")
            self.error = info.info['error']
            self.__work_file.state = 0
            self.__work_file.error = self.error
            self.__work_file.save()
            return False
        logger.info(f"File {self.__log_name} get info success")
        self.__work_file.codec = info.info['codec']
        self.__work_file.method = info.info['method']
        self.__work_file.options = info.info['options']
        # Rebuild file
        file_options = [self.__work_file.name, self.__work_file.id, self.__work_file.lang_orig.id, info.info['method'], info.info['options']]
        logger.info('Build marks for file {}(id:{}) language: {} method: {} options: {}'.format(*file_options))
        file_rebuilder = FileRebuild(self.__work_file.data.path, info.info['codec'], *file_options)
        if file_rebuilder.error:
            logger.warning(f"File {self.__log_name} build marks error: {file_rebuilder.error}")
            self.error = file_rebuilder.error
            self.__work_file.state = 0
            self.__work_file.error = self.error
            self.__work_file.save()
            return False
        logger.info(f"File {self.__log_name} rebuild success")
        self.__work_file.state = 2
        self.__work_file.words = file_rebuilder.stats['words']
        self.__work_file.items = file_rebuilder.stats['items']
        self.__work_file.save()
        return True

    def create_mark_translate(self, translator_id, mark_id, lang_id, text, md5sum=None, **kwargs):
        """ Create or update translates. Update translate progress. If finished - create translate file. """
        # TODO: Log translates
        if not self.__work_file:
            self.error = self.error if self.error else 'unknown'    # Error must be already set
        elif not mark_id or not lang_id or not translator_id:
            self.error = "Request params error"
        # Can't change original text
        elif lang_id == self.__work_file.lang_orig.id:
            # TODO: permissions check - mb owner can change ?
            self.error = "Can't change original text"
        # Check lang_translate in list of need translate languages
        elif lang_id not in self.__work_file.translated_set.values_list("id", flat=True):
            self.error = "No need translate to this language"
        if self.error:
            logger.warning(f"For file {self.__log_name} create translate error: {self.error}")
            return {"err": self.error}, status.HTTP_400_BAD_REQUEST
        # Get or create translate(s)
        if md5sum:  # multi update
            # Check if translates exist with same md5
            translates = Translates.objects.filter(mark__file=self.__work_file, language=lang_id, mark__md5sum=md5sum)
            control_marks = self.__work_file.filemarks_set.filter(md5sum=md5sum)
        else:
            translates = Translates.objects.filter(mark__file=self.__work_file, language=lang_id, mark__id=mark_id)
            control_marks = self.__work_file.filemarks_set.filter(id=mark_id)
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
        if not self.__work_file:
            logger.error(f"File object check progress error: {self.error if self.error else 'unknown'}")
            return False
        try:
            progress = self.__work_file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:    # App error, must be fixed
            logger.critical(f"For file {self.__work_file.id} related translated object not found: language {lang_id}")
            return False
        how_much_translated = self.__work_file.filemarks_set.filter(Q(translates__language=lang_id), ~Q(translates__text__exact="")).count()
        progress.items = how_much_translated
        finished = False
        if self.__work_file.items != how_much_translated and self.__work_file.items < how_much_translated:
            logger.critical(f"For file {self.__log_name} translates items more then file have")
        else:
            finished = True
        progress.finished = finished
        progress.save()
        return finished

    def create_progress(self):
        """ Create related translate progress to file """
        if not self.__work_file:
            logger.error(f"File object create progress error: {self.error if self.error else 'unknown'}")
            return False
        translate_to_ids = self.__work_file.folder.project.translate_to.values_list('id', flat=True)
        objs = [Translated(file_id=self.__work_file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objs)

    def create_translated_copy(self, language):
        """ Create translation copy of the file """
        if not self.__work_file:
            logger.error(f"File object check progress error: {self.error if self.error else 'unknown'}")
            return False
        pass

    def __null_file_fields(self):
        """ Refresh database object file """
        if self.__work_file.state != 1:
            self.__work_file.words = None
            self.__work_file.items = None
            self.__work_file.codec = ''
            self.__work_file.method = ''
            self.__work_file.error = 'x'
            self.__work_file.options = None

    def save_error(self):
        """ Save error file to analyze  """
        if not self.error:
            logger.warning("Can't save error file because there are no errors")
            return False
        if not self.__work_file:
            logger.error(f"File object not set to save error: {self.error if self.error else 'unknown'}")
            return False
        try:
            error_file = ErrorFiles(error=self.error, data=self.__work_file.data)
            err_obj = error_file.save()
        except ValidationError:
            logger.error(f"Can't save error file for {self.__log_name} ")
            return False
        logger.info(f'For file {self.__log_name} created error file {err_obj.id}')
        return err_obj.id, self.error
