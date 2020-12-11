from django.core.exceptions import ObjectDoesNotExist

from core.models import TranslateChangeLog, Translate, MarkItem, FileMark


class FileRelatedModelApi:
    """ File related utility class to help while translating or parsing """

    def __init__(self, orig_lang_id: int = None, translate_to_lang_id_list: list[int] = None):
        self.__orig_lang_id: int = orig_lang_id
        self.__translate_to: list[int] = translate_to_lang_id_list

    @staticmethod
    def mark_create_or_update(file_id: int, mark_obj: dict[str, any]):
        """ Create or update FileMark and return it """
        try:
            _mark = FileMark.objects.get(file_id=file_id, fid=mark_obj['fid'])
            _mark.words = mark_obj['words']
            _mark.search_words = mark_obj['search_words']
            _mark.context = mark_obj['context']
            _mark.save()
        except ObjectDoesNotExist:
            _mark = FileMark.objects.create(
                file_id=file_id,
                fid=mark_obj['fid'],
                words=mark_obj['words'],
                search_words=mark_obj['search_words'],
                context=mark_obj['context']
            )
        return _mark

    def translate_update_or_err(self, mark_id: int, lang_id: int, mark_item: dict[str, any], warning: str) -> bool:
        """ Update Translate object while parsing incoming translated copy """
        try:
            _find = {'item__mark_id': mark_id, 'item__item_number': mark_item['item_number'], 'language': lang_id}
            translate = Translate.objects.get(**_find)
        except ObjectDoesNotExist:
            return False
        else:  # Update translate
            translate.text = mark_item['text']
            translate.warning = warning
            translate.save()
            self.__log_translate_change(translate.id, mark_item['text'])
            return True

    def translate_change_by_user(self, translate_object, text: str, user_id: int) -> None:
        """ When user change translate on UI """
        translate_object.translator_id = user_id
        translate_object.warning = ''
        translate_object.text = text
        translate_object.save()
        self.__log_translate_change(translate_object.id, text, user_id)

    def item_refresh(self, mark_id: int, item_data: dict[str, any], variants: dict[int, dict[str, any]]) -> None:
        """ Create or update MarkItem and update it's Translate set if needed """
        try:
            _item = MarkItem.objects.get(mark_id=mark_id, item_number=item_data['item_number'])
            if _item.md5sum == item_data['md5sum']:
                return  # No need to change translates if item don't changed
            _item.words = item_data['words']
            _item.md5sum = item_data['md5sum']
            _item.md5sum_clear = item_data['md5sum_clear']
            _item.save()
        except ObjectDoesNotExist:
            _item = MarkItem.objects.create(
                mark_id=mark_id,
                item_number=item_data['item_number'],
                words=item_data['words'],
                md5sum=item_data['md5sum'],
                md5sum_clear=item_data['md5sum_clear']
            )
        self.__item_refresh_translates(_item.pk, item_data['text'], variants, item_data['warning'])

    def __item_refresh_translates(self, item_id: int, text: str, md5_variants: dict[int, dict[str, any]], warning: str):
        """ Create or update Translate set for MarkItem """
        # Create translate for original language
        self.__translate_create_or_update(item_id=item_id, lang_id=self.__orig_lang_id, text=text, warning=warning)
        # Create translates for other languages
        for lang_to in self.__translate_to:
            if lang_to in md5_variants.keys():  # Try to find translates if md5 found in old
                self.__translate_create_or_update(
                    item_id=item_id,
                    lang_id=lang_to,
                    text=md5_variants[lang_to]['text'],
                    warning=f"Translate taken from id:{md5_variants[lang_to]['item_id']}"
                )
            else:  # Create empty translate if no suggestion
                self.__translate_create_or_update(item_id, lang_to, '', '')

    def __translate_create_or_update(self, item_id: int, lang_id: int, text: str, warning: str) -> None:
        """ Create or update Translate found by item and language (used in parsers - no user) """
        try:
            tr = Translate.objects.get(item_id=item_id, language_id=lang_id)
            tr.translator = None
            tr.text = text
            tr.warning = warning
            tr.save()
        except ObjectDoesNotExist:
            tr = Translate.objects.create(item_id=item_id, language_id=lang_id, text=text, warning=warning)
        self.__log_translate_change(tr.pk, text)

    @staticmethod
    def __log_translate_change(tr_id: int, text: str, user_id: int = None) -> None:
        """ Log all Translate changes """
        TranslateChangeLog.objects.create(user_id=user_id, translate_id=tr_id, text=text)
