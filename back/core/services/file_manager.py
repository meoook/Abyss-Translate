import re
import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from core.services.file_get_info import DataGetInfo
from core.models import Files, ErrorFiles, FileMarks, Translates, Translated

logger = logging.getLogger('logfile')


class LocalizeFileManager:
    """ Grouped class to manage file """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.__work_file = None
        self.__error = None
        try:
            self.__work_file = Files.objects.select_related('lang_orig').get(id=file_id)
            self.__lang_orig = self.__work_file.lang_orig
        except ObjectDoesNotExist:
            logger.warning(f"File not found ID:{file_id}")

    def __get_info(self):
        """ Get codec and check original language texts exist in file """
    
    def parse(self):
        """ Get file info then parse """
        if not self.__work_file:
            logger.warning(f"Set file before parsing")
            return False
        logger.info(f"Starting parse file ID: {self.__work_file.id}")
        get_info = DataGetInfo(self.__work_file.data.read(), self.__lang_orig.short_name)
        if get_info.info['error']:
            logger.warning(f"Error getting info from file ID: {self.__work_file.id}")
            self.__error = get_info.info['error']
            return False

    def save_error(self):
        """ Save error file to analyze  """
        if not self.__error:
            logger.warning("Can't save error file because there are no errors")
            return False
        try:
            error_file = ErrorFiles(error=self.__error, data=self.__work_file.data)
            error_file.save()
        except ValidationError:
            logger.error("Can't save error file")
            return False
        return True

