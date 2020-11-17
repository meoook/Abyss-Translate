import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from core.services.file_interface.file_find_item import FileItemsFinder
from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_ue import LocalizeUEReader

from core.models import TranslateChangeLog, Translate, File, Translated, MarkItem, FileMark, ErrorFiles, Language

logger = logging.getLogger('django')


class FileModelBasicApi:
    """ Api with file model and sub models(file-mark-item-translate-log) """

    def __init__(self, file_id):
        """ Get file object from database to do other actions """
        # Object flags and params
        self._log_name = ''
        # Init
        try:
            # self._file = File.objects.select_related('lang_orig').get(id=file_id)
            self._file = File.objects.get(id=file_id)
        except ObjectDoesNotExist:
            self._handle_err(f"File not found ID: {file_id}")
        except Exception as exc:
            self._handle_err(f"Unknown exception while getting file object. ID: {file_id} exception: {exc}", 2)
        else:
            # Object flags and params
            # self._lang_orig = self._file.lang_orig
            self._log_name = f'{self._file.name}(id:{self._file.id})'
            self._structure_changed = False   # Flag to check if file structure have changed  FIXME - not used

    @staticmethod
    def __fid_lookup_formula_exist(info):
        """ If no formula - don't check by fID when parsing file """
        if info.method in ['csv', 'ue']:
            if not info.options['fid_lookup']:
                return False
        return True

    @staticmethod
    def __log_translate(tr_id, text, user_id=None):
        TranslateChangeLog.objects.create(user_id=user_id, translate_id=tr_id, text=text)

    def _tr_change_by_user(self, translate_object, text, user_id):
        """ By id can be changed only by user_id """
        translate_object.translator_id = user_id
        translate_object.text = text
        translate_object.save()
        self.__log_translate(translate_object.id, text, user_id)

    def __tr_up_or_cr_by_parser(self, item_id, lang_id, text, warning):
        """ Change or create translate and empty translates for other language """
        try:
            tr = Translate.objects.get(item_id=item_id, language_id=lang_id)
            tr.text = text
            tr.warning = warning
            tr.save()
        except ObjectDoesNotExist:
            tr = Translate.objects.create(item_id=item_id, language_id=lang_id, text=text, warning=warning)
        self.__log_translate(tr.pk, text)

    def __tr_refresh_by_parser_for_languages(self, item_id, orig_lang_id, lang_list, text, md5_lang_variants, warning):
        # Create translate for original language
        self.__tr_up_or_cr_by_parser(item_id=item_id, lang_id=orig_lang_id, text=text, warning=warning if warning else '')
        # Create translates for other languages
        for lang_to in lang_list:
            if lang_to in md5_lang_variants.keys():  # Try to find translates if md5 found in old
                self.__tr_up_or_cr_by_parser(item_id=item_id, lang_id=lang_to, text=md5_lang_variants[lang_to]['text'],
                                             warning=f"Translate taken from id:{md5_lang_variants[lang_to]['item_id']}")
            else:  # Create empty translate if no suggestion
                self.__tr_up_or_cr_by_parser(item_id, lang_to, '', '')

    def _file_rebuild_original(self, orig_id, languages_to, info_obj):
        """ Update, delete, insert translates while parsing file -> then refresh file stats """
        if not self.__fid_lookup_formula_exist(info_obj):
            logger.info(f'File {self._log_name} don\'t have fID formula and will build by index')

        reader = self._get_reader(info_obj)
        finder = FileItemsFinder(self._file.id)  # Prepare finder and remember old marks
        for file_mark in reader:
            # Getting FileMark object
            try:
                mark = FileMark.objects.get(file_id=self._file.id, fid=file_mark['fid'])
                mark.words = file_mark['words']
                mark.search_words = file_mark['search_words']
                mark.context = file_mark['context']
                mark.save()
                mark_updated = False
            except ObjectDoesNotExist:
                if not self._structure_changed:
                    logger.info('structure not changed but new mark')
                mark = FileMark.objects.create(file_id=self._file.id, fid=file_mark['fid'],
                                               words=file_mark['words'], search_words=file_mark['search_words'],
                                               context=file_mark['context'],)
                mark_updated = True
            finder.used_mid = mark.id  # add mark id not to delete
            numbers_not_to_delete = []  # After adding items - delete old unused if structure changed
            for mark_item in file_mark['items']:
                numbers_not_to_delete.append(mark_item['item_number'])
                warning = mark_item['warning']
                # if mark_updated:
                # Getting MarkItem object
                try:
                    _item = MarkItem.objects.get(mark=mark, item_number=mark_item['item_number'])
                    if _item.md5sum == mark_item['md5sum']:
                        continue  # No need to change translates if item don't changed
                    _item.words = mark_item['words']
                    _item.md5sum = mark_item['md5sum']
                    _item.md5sum_clear = mark_item['md5sum_clear']
                    _item.save()
                    item_updated = True
                except ObjectDoesNotExist:
                    if not self._structure_changed:
                        _msg_detail = f"mark:{mark.id} number:{mark_item['item_number']}"
                        self._handle_err(f'structure not changed but item not found {_msg_detail}', 2)
                        warning = 'item not common for structure'
                    _item = MarkItem.objects.create(mark=mark, item_number=mark_item['item_number'],
                                                    words=mark_item['words'], md5sum=mark_item['md5sum'],
                                                    md5sum_clear=mark_item['md5sum_clear'])
                # Prepare translates to find by inner text (old translates in DB)
                translates_with_text = finder.find_by_md5(mark_item['md5sum'])
                # Create/update translates - For optimisation we save languages before
                self.__tr_refresh_by_parser_for_languages(_item.pk, orig_id, languages_to,
                                                          mark_item['text'], translates_with_text, warning)
            # Delete old items if mark updated
            delete_amount, _ = mark.markitem_set.exclude(item_number__in=numbers_not_to_delete).delete()
            if delete_amount and not self._structure_changed:  # Can not be new items if structure don't change
                self._handle_err(f'structure not changed but was {delete_amount} items to delete', 2)
        # Delete unused marks
        _amount, _ = self._file.filemark_set.exclude(id__in=finder.used_mid).delete()
        logger.info(f"File {self._log_name} delete {_amount} unused marks")
        # Save results
        self._file.error = ''
        self._file.items, self._file.words = reader.stats
        self._file.save()
        logger.info(f"File {self._log_name} build as original success")

    def _file_rebuild_translates(self, lang_id, info_obj):
        """ Update, delete, insert translates while parsing file for selected language then update progress """
        if self.__fid_lookup_formula_exist(info_obj):
            warning = ''
        else:
            warning = 'translate placed by file index'  # TODO: It ok to change translate without formula ?
            self._handle_err('translate copy don\'t have fID formula and will build by index')

        reader = self._get_reader(info_obj)
        for file_mark in reader:
            try:
                mark = self._file.filemark_set.get(fid=file_mark['fid'])
            except ObjectDoesNotExist:
                continue
            else:
                for mark_item in file_mark['items']:
                    try:
                        _find = {'item__mark': mark, 'item__item_number': mark_item['item_number'], 'language': lang_id}
                        translate = Translate.objects.get(**_find)
                    except ObjectDoesNotExist:
                        self._handle_err(f"can't find translate for fID:{file_mark['fid']} to fill language:{lang_id}")
                        continue
                    else:  # Update translate
                        translate.text = mark_item['text']
                        translate.warning = warning
                        translate.save()
                        self.__log_translate(translate.id, mark_item['text'])
        logger.info(f"File {self._log_name} build as copy success")

    def _file_progress_create(self):
        """ Create progress for 'new' file """
        logger.info(f"File {self._log_name} creating progress for all languages")
        translate_to_ids = [x for x in self._file.folder.project.translate_to.values_list('id', flat=True)]
        objects_to_create = [Translated(file_id=self._file.id, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objects_to_create)
        return translate_to_ids

    def _file_progress_refresh(self, lang_id):
        """ Refresh file progress for language """
        try:
            progress = self._file.translated_set.get(language=lang_id)
        except ObjectDoesNotExist:  # App error, must be fixed
            self._handle_err(f'related translated object not found for language:{lang_id}', 2)
            return False
        translated_items_amount = MarkItem.objects.filter(mark__file_id=self._file.id) \
            .filter(Q(translate__language=lang_id), ~Q(translate__text__exact="")).count()
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
        for translated in self._file.translated_set.all():
            self._file_progress_refresh(translated.language)

    def _handle_err(self, err_msg, lvl=0):
        msg = f"File {self._log_name} - {err_msg}" if self._log_name else err_msg
        if lvl == 2:
            logger.critical(msg)
        elif lvl == 1:
            logger.error(msg)
        else:
            logger.warning(msg)
        # raise AssertionError(msg)

    @staticmethod
    def _get_reader(info_obj, copy_path=''):
        """ Get parser for method """
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

    @staticmethod
    def _get_lang_short_name(lang_id):
        try:
            return Language.objects.get(id=lang_id).short_name
        except ObjectDoesNotExist:
            return ''
