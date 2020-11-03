import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_ue import LocalizeUEReader

from core.models import TranslateChangeLog, Translate, File, Translated, MarkItem

logger = logging.getLogger('django')


class FileModelBasicApi:
    """ Api with file model and utils """
    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        # Object flags and params
        self._log_name = ''
        # Init
        try:
            self._file = File.objects.select_related('lang_orig').get(id=file_id)
        except ObjectDoesNotExist:
            self._handle_err(f"File not found ID: {file_id}")
        except Exception as exc:
            self._handle_err(f"Unknown exception while getting file object. ID: {file_id} exception: {exc}", 2)
        else:
            self._lang_orig = self._file.lang_orig
            self._log_name = f'{self._file.name}(id:{self._file.id})'

    @staticmethod
    def __log_translate(tr_id, text, user=None):
        TranslateChangeLog.objects.create(user_id=user, translate_id=tr_id, text=text)

    def __translate_change(self, trans_obj, text, user=None):
        """ Change text in translate and log by this user (no user = system) """
        trans_obj.update(text=text)
        self.__log_translate(trans_obj.id, text, user)

    def _tr_change_by_user(self, tr_id, text, user):
        """ By id can be changed only by user """
        try:
            translate = Translate.objects.get(id=tr_id)
        except ObjectDoesNotExist:
            self._handle_err("Translate not found ID: " + tr_id)
            return False
        self.__translate_change(translate, text, user)

    def _tr_change_by_parser(self, fid, item_number, lang_id, text):
        """ Same as _change_translate but find translate by fid, number and language """
        try:
            translate = Translate.objects.get(item__mark_fid=fid, item__item_number=item_number, language_id=lang_id)
        except ObjectDoesNotExist:
            self._handle_err(f"Translate not found for item:{fid} number:{item_number} language:{lang_id}")
        else:
            self.__translate_change(translate, text)

    def _tr_create_by_parser(self, item_id, lang_id, text, warning):
        """ Crate translate and empty translates for other language """
        tr = Translate.objects.create(item_id=item_id, language_id=lang_id, text=text, warning=warning)
        self.__log_translate(tr.pk, text)

    def _add_mark(self, item):
        """ item taken from parsers and have const structure """
        pass

    def _change_file(self, file_id, kwargs):
        """ change file with new field: value """
        pass

    def _file_progress_create(self):
        """ create progress for new file """
        translate_to_ids = self._file.folder.project.translate_to.values_list('id', flat=True)
        objects_to_create = [Translated(file_id=self._file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objects_to_create)

    def __file_progress_refresh(self, lang_id):
        """ Refresh file progress for language """
        try:
            progress = self._file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            self._handle_err('For file {} related translated object not found: language ' + lang_id, 2)
            return False
        translated_items_amount = MarkItem.objects.filter(mark__file_id=self._file.id)\
            .filter(Q(translates__language=lang_id), ~Q(translates__text__exact="")).count()
        progress.items = translated_items_amount
        progress.save()
        if self._file.items != translated_items_amount:
            if self._file.items < translated_items_amount:
                self._handle_err("For file {} translates items more then file have", 2)
            return False
        return True

    def _file_progress_refresh_all(self):
        """ Refresh file progress for all languages """
        for lang in self._file.translated_set.all():
            self.__file_progress_refresh(lang.id)

    def _handle_err(self, err_msg, lvl=0):
        msg = err_msg.format(self._log_name) if self._log_name else err_msg
        if lvl == 2:
            logger.critical(msg)
        elif lvl == 1:
            logger.error(msg)
        else:
            logger.warning(msg)
        raise AssertionError(msg)

    @staticmethod
    def _get_reader(info_obj):
        reader_params = [info_obj.data, info_obj.codec, info_obj.options]
        assert info_obj.method not in ['csv', 'html', 'ue'], "Unknown method to read file"
        if info_obj.method == 'csv':
            return LocalizeCSVReader(*reader_params)
        elif info_obj.method == 'html':
            return LocalizeHtmlReader(*reader_params)
        elif info_obj.method == 'ue':
            return LocalizeUEReader(*reader_params)
