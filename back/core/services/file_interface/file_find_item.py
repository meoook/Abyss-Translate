from core.models import Translate


class FileItemsFinder:
    """ Fill items by md5 in current DB state. Also control fIDs not to delete. """
    def __init__(self, file_id: int):
        assert isinstance(file_id, int), f"File id must be int but {type(file_id)}"
        self.__items_to_check: dict[str, dict[int, dict[str, any]]] = {}  # {md5: {lang_id: {item_id, text} } }
        self.__marks_ids_not_to_del: list[int] = []

        self.__fill_check_objects(file_id)

    @property
    def used_mid(self) -> list[int]:
        return self.__marks_ids_not_to_del

    @used_mid.setter
    def used_mid(self, value: int):
        self.__marks_ids_not_to_del.append(value)

    def find_by_md5(self, md5: str) -> dict[int, dict[str, any]]:
        """ List of md5:text """
        if md5 in self.__items_to_check.keys():
            return self.__items_to_check[md5]
        return {}

    def __fill_check_objects(self, file_id: int) -> None:
        """ Prepare data - get file translates to selected language """
        fields = ('item_id', 'text', 'language_id', 'item__md5sum', 'item__md5sum_clear')
        for tr_obj in Translate.objects.filter(item__mark__file_id=file_id).values(*fields):
            self.__add_item(tr_obj['item__md5sum'], tr_obj['item_id'], tr_obj['language_id'], tr_obj['text'])
            self.__add_item(tr_obj['item__md5sum_clear'], tr_obj['item_id'], tr_obj['language_id'], tr_obj['text'])

    def __add_item(self, md5: str, item_id: int, lang_id: int, text: str) -> None:
        """ Taken flag needed to check if to create new object or no """
        if text:
            if md5 not in self.__items_to_check.keys():  # Filter duplicates
                self.__items_to_check[md5] = {lang_id: {'text': text, 'item_id': item_id}, }
            elif lang_id not in self.__items_to_check[md5]:  # Replace with text inside
                self.__items_to_check[md5][lang_id] = {'text': text, 'item_id': item_id}
