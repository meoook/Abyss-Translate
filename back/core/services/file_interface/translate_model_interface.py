from django.core.exceptions import ObjectDoesNotExist

from core.models import TranslateChangeLog, Translate, MarkItem


class TranslateModelApi:
    """ Class to help while translating or parsing """
    def __init__(self, structure_changed: bool, orig_lang_id: int = None, translate_to_lang_id_list: list[int] = None):
        self.__structure_changed: bool = structure_changed
        self.__orig_lang_id: int = orig_lang_id
        self.__translate_to: list[int] = translate_to_lang_id_list

    @staticmethod
    def tr_logger(tr_id: int, text: str, user_id: int = None) -> None:
        TranslateChangeLog.objects.create(user_id=user_id, translate_id=tr_id, text=text)

    def tr_change_by_user(self, translate_object, text: str, user_id: int) -> None:
        """ When user change translate on UI """
        translate_object.translator_id = user_id
        translate_object.warning = ''
        translate_object.text = text
        translate_object.save()
        self.tr_logger(translate_object.id, text, user_id)

    def item_refresh_translates(self, item_id: int, text: str, md5_variants: dict[int, dict[str, any]], warning: str):
        """ Refresh item translates """
        # Create translate for original language
        self.__tr_create_or_update(item_id=item_id, lang_id=self.__orig_lang_id, text=text, warning=warning)
        # Create translates for other languages
        for lang_to in self.__translate_to:
            if lang_to in md5_variants.keys():  # Try to find translates if md5 found in old
                self.__tr_create_or_update(item_id=item_id, lang_id=lang_to, text=md5_variants[lang_to]['text'],
                                           warning=f"Translate taken from id:{md5_variants[lang_to]['item_id']}")
            else:  # Create empty translate if no suggestion
                self.__tr_create_or_update(item_id, lang_to, '', '')

    def __tr_create_or_update(self, item_id: int, lang_id: int, text: str, warning: str):
        """ Change or create translate by item and language (used in parsers - no user) """
        try:
            tr = Translate.objects.get(item_id=item_id, language_id=lang_id)
            tr.translator = None
            tr.text = text
            tr.warning = warning
            tr.save()
        except ObjectDoesNotExist:
            tr = Translate.objects.create(item_id=item_id, language_id=lang_id, text=text, warning=warning)
        self.tr_logger(tr.pk, text)

    def item_refresh(self, mark_id: int, item_data: dict[str, any]):
        """ Create or update mark item and update translates for it if needed """
        try:
            _item = MarkItem.objects.get(mark_id=mark_id, item_number=item_data['item_number'])
            if _item.md5sum == item_data['md5sum']:  # No need to change translates if item don't changed
                return _item, 'same'
            _item.words = item_data['words']
            _item.md5sum = item_data['md5sum']
            _item.md5sum_clear = item_data['md5sum_clear']
            _item.save()
            return _item, 'new'
        except ObjectDoesNotExist:
            if not self.__structure_changed:
                _msg_detail = f"mark:{mark_id} number:{item_data['item_number']}"
                self._handle_err(f'structure not changed but item not found {_msg_detail}', 2)
                warning = 'item not common for structure'
            _item = MarkItem.objects.create(mark_id=mark_id, item_number=item_data['item_number'],
                                            words=item_data['words'], md5sum=item_data['md5sum'],
                                            md5sum_clear=item_data['md5sum_clear'])
            return _item, 'created'
