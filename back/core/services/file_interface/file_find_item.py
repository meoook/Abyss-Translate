from core.models import Translate, FileMark


class FileItemsFinder:
    """ Find mark id or item id by fid or md5 """

    def __init__(self, file_id, fid_lookup_exist, is_original_lang=True):
        assert isinstance(file_id, int), f"File id must be int but {type(file_id)}"
        if not fid_lookup_exist and not is_original_lang:
            raise AssertionError("Can't fill translates without fID lookup formula")
        self.__is_original = is_original_lang
        self.__formula_exist = fid_lookup_exist
        self.__marks_to_check = {}  # by fid
        self.__items_to_check = {}  # by md5

        self.__fill_check_objects(file_id)

    @property
    def unused_fid(self):
        """ If value True - it means it been taken in find_by_fid method """
        return [key for key, value in self.__marks_to_check.items() if not self.__marks_to_check[key]]

    def find_by_fid(self, fid):
        if self.__formula_exist:
            if fid in self.__marks_to_check.keys():
                self.__marks_to_check[fid] = True  # Mark was taken
                return True
        return False

    def find_by_md5(self, md5):
        if self.__is_original and md5 in self.__items_to_check.keys():
            return self.__items_to_check[md5]
        return {}

    def __fill_check_objects(self, file_id):
        """ Prepare data - get file translates to selected language """
        if self.__formula_exist:  # No need to check exist status -> [fid:number] - unique
            for mark_obj in FileMark.objects.filter(file_id=file_id).values('id', 'fid'):
                self.__marks_to_check[mark_obj.fid] = False  # Mark was not taken
        if self.__is_original:  # For original language we can find texts by md5
            fields = ('item_id', 'text', 'language_id', 'item__md5sum', 'item__md5sum_clear')
            for tr_obj in Translate.objects.filter(item__mark__file_id=file_id).values(*fields):
                self.__add_item(tr_obj.item__md5sum, tr_obj.item_id, tr_obj.language_id, tr_obj.text)
                self.__add_item(tr_obj.item__md5sum_clear, tr_obj.item_id, tr_obj.language_id, tr_obj.text)

    def __add_item(self, md5, item_id, lang_id, text):
        """ Taken flag needed to check if to create new object or no """
        if text:
            if md5 not in self.__items_to_check.keys():  # Filter duplicates
                self.__items_to_check[md5] = {lang_id: {'text': text, 'item_id': item_id}, }
            elif not self.__items_to_check[md5][lang_id]:  # Replace with text inside
                self.__items_to_check[md5][lang_id] = {'text': text, 'item_id': item_id}
