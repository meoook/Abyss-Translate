from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.parser_utils import ParserUtils


class LocalizeRowReader(ParserUtils):
    """ Read file and yield FileMark object for each row to insert in DB. Also control creating translation copy. """

    def __init__(self, decoded_data: str, data_codec: str, _, copy_path: str = ''):
        self.__data: list[str] = decoded_data.splitlines()
        self.__serializer = _RowToMarkSerializer(data_codec)
        self.__row_index: int = 0
        self.__max_index: int = len(self.__data) - 1
        # File results
        self.__file_items: int = 0
        self.__file_words: int = 0
        # If copy path set - create CCC object to control copy creation
        self.__copy = CopyContextControl(copy_path, data_codec) if copy_path else None

    @property
    def stats(self) -> tuple[int, int]:
        return self.__file_items, self.__file_words

    def __iter__(self):
        return self

    def __next__(self) -> dict[str, any]:
        if self.__row_index > self.__max_index:
            if self.__copy:  # handle copy control
                self.__copy.finish()  # To finish file
            raise StopIteration
        if self.__copy:  # handle copy control
            self.__copy.add_data(self.__data[self.__row_index])

        mark_obj = self.__serializer.serialize(self.__data[self.__row_index])
        self.__row_index += 1
        if not mark_obj['words']:
            self.__next__()
        self.__file_items += 1  # Each mark have only one item for this method
        self.__file_words += mark_obj['words']
        # return {**mark_obj, 'fid': self.__row_index}
        return mark_obj | {'fid': self.__row_index}

    def copy_write_mark_items(self, values: list[dict[str, any]]) -> None:
        """ Write translates in translation file copy file for current item """
        if self.__copy:  # handle copy control
            to_add = values[0]['text']
            self.__copy.replace_and_save(to_add)


class _RowToMarkSerializer(ParserUtils):
    """ Row to mark serializer """
    def __init__(self, codec: str):
        self.__codec: str = codec

    def serialize(self, row_text: str) -> dict[str, any]:
        clean_text: str = self._clean_text(row_text)
        item_words: int = self._count_words(clean_text)
        items: list[dict[str, any]] = []

        if item_words > 0:
            items.append({
                'item_number': 1,
                'md5sum': self._get_md5(row_text.encode(self.__codec)),
                'md5sum_clear': self._get_md5(clean_text.encode(self.__codec)),
                'words': item_words,
                'text': row_text,
                'warning': None,
            })

        return {
            'words': item_words,
            'items': items,
            'search_words': clean_text.lower(),
            'context': clean_text,
        }
