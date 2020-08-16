import re
import logging

from core.models import Files, FileMarks, Translates, Translated

logger = logging.getLogger('logfile')


class LocalizeFileManager:
    """ Grouped class to manage file """

    def __init__(self, file_id):

        work_file = Files.objects.select_related('lang_orig').get(id=file_id)

