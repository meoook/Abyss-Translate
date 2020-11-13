import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from core.services.file_interface.file_find_item import FileItemsFinder
from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_ue import LocalizeUEReader

from core.models import TranslateChangeLog, Translate, File, Translated, MarkItem, FileMark, ErrorFiles

logger = logging.getLogger('django')


class FileModelBasicApi:
    """ Api with file model and sub models(file-mark-item-translate-log) """

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
            self._fid_lookup_exist = self._fid_lookup_formula_exist

    @property
    def _fid_lookup_formula_exist(self):
        """ If no formula - don't check by fID when parsing file """
        if self._file.method in ['csv', 'ue']:
            if not self._file.options['fid_lookup']:
                return False
        return True

    @staticmethod
    def __log_translate(tr_id, text, user_id=None):
        TranslateChangeLog.objects.create(user_id=user_id, translate_id=tr_id, text=text)

    def __translate_change(self, trans_obj, text, user_id=None):
        """ Change text in translate and log by this user_id (no user_id = system) """
        trans_obj.text = text
        trans_obj.save()
        self.__log_translate(trans_obj.id, text, user_id)

    # def _tr_change_by_user(self, tr_id, text, user_id):
    #     """ By id can be changed only by user_id """
    #     try:
    #         translate = Translate.objects.get(id=tr_id)
    #     except ObjectDoesNotExist:
    #         self._handle_err("Translate not found ID: " + tr_id)
    #         return False
    #     self.__translate_change(translate, text, user_id)

    def _tr_change_by_fid(self, fid, item_number, lang_id, text):
        """ Find translate by fid, number and language and change it text field """
        try:
            translate = Translate.objects.get(item__mark__fid=fid, item__item_number=item_number, language_id=lang_id)
        except ObjectDoesNotExist:
            self._handle_err(f"Translate not found for item:{fid} number:{item_number} language:{lang_id}", 2)
            # translate = Translate.objects\
            #     .create(item__mark_fid=fid, item__item_number=item_number, language_id=lang_id, text=text)
            # self.__log_translate(translate.id, text)
        else:
            self.__translate_change(translate, text)

    def _tr_create_by_parser(self, item_id, lang_id, text, warning):
        """ Change or create translate and empty translates for other language """
        tr = Translate.objects.create(item_id=item_id, language_id=lang_id, text=text, warning=warning)
        self.__log_translate(tr.pk, text)

    def _file_build_translates(self, info_obj, lang_id):
        """ Update, delete, insert translates while parsing file for selected language then update progress """
        orig_id = self._lang_orig.id
        is_original = orig_id == lang_id  # Bonus methods to original file

        if not self._fid_lookup_exist and not is_original:
            self._handle_err('File {} can\'t don\'t have fID formula and can\'t be translated to language:' + lang_id)
            return False

        reader = self._get_reader(info_obj)
        finder = FileItemsFinder(self._file.id, self._fid_lookup_exist, is_original)  # Prepare finder

        for file_mark in reader:
            if self._fid_lookup_exist:
                print('FID FORMULA EXIST', file_mark['fid'])
                # For fid - use change method
                if finder.find_by_fid(file_mark['fid']):
                    for item in file_mark['items']:
                        self._tr_change_by_fid(file_mark['fid'], item['item_number'], lang_id, item['text'])
                    continue
                else:
                    print('NOT FOUND FID IN OLD FIDs')

            if is_original:  # For original language try to find translated texts(all lang) in current translates
                # Anyway create new mark and translates - old will be deleted
                mark = FileMark(
                    file_id=self._file.id,
                    fid=file_mark['fid'],
                    words=file_mark['words'],
                    search_words=file_mark['search_words'],
                    context=file_mark['context'],
                )
                mark.save()
                for mark_item in file_mark['items']:
                    item_obj = MarkItem(mark=mark, item_number=mark_item['item_number'], words=mark_item['words'],
                                        md5sum=mark_item['md5sum'], md5sum_clear=mark_item['md5sum_clear'])
                    item_obj.save()  # Create mark items
                    # Prepare translates to find by inner text
                    translates_with_text = finder.find_by_md5(mark_item['md5sum'])
                    # Crate translate and empty translates for other language (with logging)
                    for lang_to_tr in [orig_id, *self._file.folder.project.translate_to.values_list('id', flat=True)]:
                        # For selected lang - translates taken from file
                        if lang_to_tr == lang_id:
                            self._tr_create_by_parser(item_id=item_obj.pk, lang_id=lang_to_tr, text=mark_item['text'],
                                                      warning=mark_item['warning'] if mark_item['warning'] else '')
                        elif lang_to_tr in translates_with_text.keys():
                            # For other languages - look in old translates (in DB)
                            if mark_item['warning']:  # Set warning for translates that found by md5
                                warning = mark_item['warning']
                            else:
                                warning = f"Translate taken from id:{translates_with_text[lang_to_tr]['item_id']}"
                            self._tr_create_by_parser(item_id=item_obj.pk, lang_id=lang_to_tr,
                                                      text=translates_with_text[lang_to_tr]['text'],
                                                      warning=warning)
                        else:  # Create empty translate if no suggestion
                            self._tr_create_by_parser(item_obj.pk, lang_to_tr, '', '')
            else:
                self._handle_err("Can't fill translates without fID formula - {}")
        if is_original:
            # Delete unused marks
            logger.info(f"File {self._log_name} delete unused marks")
            self._file.filemark_set.filter(fid__in=finder.unused_fid).delete()
            # Save results
            self._file.error = ''
            self._file.items, self._file.words = reader.stats
            self._file.save()
            logger.info(f"File {self._log_name} build as original success")
            # No need to refresh progress for original language (call 'refresh_all' only when file updated 'not new')
        else:
            logger.info(f"File {self._log_name} build as copy success")

    def _file_progress_up_or_cr(self):
        """ Update file progress or create if not exist """
        if self._file.translated_set.count() > 0:
            self._file_progress_refresh_all()
        else:
            self._file_progress_create()

    def _file_progress_create(self):
        """ create progress for new file """
        logger.info(f"File {self._log_name} creating progress for all languages")
        translate_to_ids = self._file.folder.project.translate_to.values_list('id', flat=True)
        objects_to_create = [Translated(file_id=self._file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objects_to_create)

    def _file_progress_refresh(self, lang_id):
        """ Refresh file progress for language """
        try:
            progress = self._file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            self._handle_err('For file {} related translated object not found: language ' + lang_id, 2)
            return False
        translated_items_amount = MarkItem.objects.filter(mark__file_id=self._file.id) \
            .filter(Q(translates__language=lang_id), ~Q(translates__text__exact="")).count()
        progress.items = translated_items_amount
        progress.save()
        logger.info(f"File {self._log_name} progress refresh for language:{lang_id}")
        if self._file.items != translated_items_amount:
            if self._file.items < translated_items_amount:
                self._handle_err("For file {} translates items:" + translated_items_amount + " more then file have", 2)
            return False
        return True

    def _file_progress_refresh_all(self):
        """ Refresh file progress for all languages """
        for lang in self._file.translated_set.all():
            self._file_progress_refresh(lang.id)

    def _handle_err(self, err_msg, lvl=0):
        msg = err_msg.format(self._log_name) if self._log_name else err_msg
        if lvl == 2:
            logger.critical(msg)
        elif lvl == 1:
            logger.error(msg)
        else:
            logger.warning(msg)
        # raise AssertionError(msg)

    @staticmethod
    def _get_reader(info_obj, copy_path=''):
        reader_params = [info_obj.data, info_obj.codec, info_obj.options]
        assert info_obj.method in ['csv', 'html', 'ue'], "Unknown method to read file"
        if info_obj.method == 'csv':
            return LocalizeCSVReader(*reader_params, copy_path=copy_path)
        elif info_obj.method == 'html':
            return LocalizeHtmlReader(*reader_params, copy_path=copy_path)
        elif info_obj.method == 'ue':
            return LocalizeUEReader(*reader_params, copy_path=copy_path)

    def _save_error(self):
        """ Save error file to analyze  """
        err_file_name = f'err_{self._file.id}.txt'
        try:
            err_file_path = settings.STORAGE_ERRORS.save(err_file_name, self._file.data)
            error_file = ErrorFiles(error=self._file.error, data=err_file_path)
            error_file.save()
        except ValidationError:
            logger.error(f"Can't save error file for {self._log_name} ")
            return False
        logger.info(f'For file {self._log_name} created error file {err_file_name}:{error_file.pk}')
        return error_file.pk
