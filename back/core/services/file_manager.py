import re
import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from core.models import Files, ErrorFiles, FileMarks, Translates, Translated

from core.services.file_get_info import DataGetInfo
from core.services.file_rebuild import FileRebuild

logger = logging.getLogger('logfile')


class LocalizeFileManager:
    """ Grouped class to manage file """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.success = False
        self.__work_file = None
        self.__error_file_msg = None
        try:
            self.__work_file = Files.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            logger.warning(f"File not found ID: {file_id}")
        except Exception as exc:
            logger.critical(f"Uknown exception while getting file object. ID: {file_id} exception: {exc}")
        else:
            self.success = True
            self.__lang_orig = self.__work_file.lang_orig
            self.__log_name = f'{self.__work_file.name}(id:{self.__work_file.id})'
            self.__data_binary = self.__work_file.data.read()

    def parse(self):
        """ Get file info then parse """
        if not self.__work_file:
            logger.warning(f"Set file before parsing")
            return False
        logger.info(f"Starting parse file ID: {self.__work_file.id}")
        # Null file object fields
        self.__null_file_fields()
        # Get codec, parse method and check original language texts exist in file 
        info = DataGetInfo(self.__data_binary, self.__lang_orig.short_name)
        if info.info['error']:
            logger.warning(f"File {self.__log_name} get info error: {info.info['error']}")
            self.__error_file_msg = info.info['error']
            self.__work_file.save(state=0, error=info.info['error'])
            return False
        logger.info(f"File {self.__log_name} get info success")
        self.__work_file.codec = info.info['codec']
        self.__work_file.method = info.info['method']
        self.__work_file.options = info.info['options']
        # Rebuild file
        file_options = [self.__work_file.name, self.__work_file.id, self.__work_file.lang_orig, info.info['method'], info.info['options']]
        logger.info('Build marks for file {}(id:{}) language: {} method: {} options: {}'.format(*file_options))
        file_rebuilder = FileRebuild(self.__work_file.data.path, info.info['codec'], *file_options)
        if file_rebuilder.error:
            logger.warning(f"File {self.__log_name} build error: {info.info['error']}")
            self.__work_file.state = 0
            self.__error_file_msg = file_rebuilder.error
            self.__work_file.save(state=0, error=file_rebuilder.error)
            return False
        logger.info(f"File {self.__log_name} rebuild success")
        self.__work_file.state = 2
        self.__work_file.words = file_rebuilder.stats['words']
        self.__work_file.items = file_rebuilder.stats['items']
        self.__work_file.save()
        return True
    
    def create_translation(self, language):
        """ Create translation copy of the file """
        pass

    def __null_file_fields(self):
        """ Refresh database object file """
        if self.__work_file.state != 1:
            self.__work_file.words = None
            self.__work_file.items = None
            self.__work_file.codec = ''
            self.__work_file.method = ''
            self.__work_file.error = ''
            self.__work_file.options = None

    def save_error(self):
        """ Save error file to analyze  """
        if not self.__error_file_msg:
            logger.warning("Can't save error file because there are no errors")
            return False
        try:
            logger.info(f'Saving error file {self.__log_name}')
            error_file = ErrorFiles(error=self.__error_file_msg, data=self.__work_file.data)
            error_file.save()
        except ValidationError:
            logger.error(f"Can't save error file for {self.__log_name} ")
            return False
        return True

