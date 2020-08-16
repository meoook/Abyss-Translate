import re
import logging

from core.models import Files, FileMarks, Translates, Translated
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('logfile')


class LocalizeFileManager:
    """ Grouped class to manage file """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        self.__work_file = None
        try:
            self.__work_file = Files.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            logger.warning(f"File not found ID:{file_id}")
    
    def parse():
        """ Get file info then parse """
        if not self.__work_file:
            logger.warning(f"Try to parse not existing file")
            return False
        

