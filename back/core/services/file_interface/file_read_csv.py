from typing import Callable

from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.id_finder import UniqueIDLookUp
from core.services.file_interface.parser_utils import ParserUtils
from core.services.file_interface.quote_finder import TextQuoteFinder


class LocalizeCSVReader:
    """ Read csv file and yield FileMark object to insert in DB. Also control creating translation copy. """

    def __init__(self, decoded_data: str, data_codec: str, scan_options: dict[str, any], copy_path: str = ''):
        self.__data: list[str] = decoded_data.splitlines()
        self.__row_parser = _CsvRowToMarkSerializer(data_codec, scan_options)
        self.__row_index: int = scan_options['top_rows']
        self.__max_index: int = len(self.__data) - 1
        # File results
        self.__file_items: int = 0
        self.__file_words: int = 0
        # If copy path set - create CCC object to control copy creation
        self.__copy = CopyContextControl(copy_path, data_codec) if copy_path else None
        if self.__copy and self.__row_index:
            for _top_row_idx in range(self.__row_index):  # Add top rows to translated copy
                self.__copy.add_data(self.__data[_top_row_idx])

    @property
    def stats(self) -> tuple[int, int]:
        return self.__file_items, self.__file_words

    def __iter__(self):
        return self

    def __next__(self) -> dict[str, any]:
        self.__next_row_with_value()
        if self.__row_index > self.__max_index:
            if self.__copy:  # handle copy control
                self.__copy.finish()  # To finish file
            raise StopIteration
        self.__file_items += len(self.__row_parser.data['items'])
        self.__file_words += self.__row_parser.data['words']
        if self.__row_parser.data['fid']:
            return self.__row_parser.data
        else:
            return self.__row_parser.data | {'fid': self.__row_index}

    def __next_row_with_value(self):
        """ Find next row where value is valid text (set row index and handle copy) """
        while self.__row_index <= self.__max_index:
            if self.__copy:  # handle copy control
                self.__copy.add_data(self.__data[self.__row_index])
            # Set next row
            self.__row_parser.data = self.__data[self.__row_index]
            self.__row_index += 1
            if self.__row_parser.data['words']:
                return

    def copy_write_mark_items(self, values: list[dict[str, any]]) -> None:
        """ Write row filled with values in translation file copy """
        if self.__copy:  # handle copy control
            to_add = self.__row_parser.fill_row_with_items(values)
            self.__copy.replace_and_save(to_add)


class _CsvRowToMarkSerializer(ParserUtils):
    """ Row to mark serializer """
    def __init__(self, codec: str, scan_options: dict[str, any]):
        self.__current_row_items: list[str] = []
        # Row parse options
        self.__codec: str = codec
        self.__delimiter: str = scan_options['delimiter']
        self.__fields: list[int] = scan_options['fields']
        # Define function to get text from quoted text
        self.__get_unquote_text: Callable[[str], str] = TextQuoteFinder.function_to_unquote_text(scan_options['quotes'])
        # Define function to get fID from formula
        self.__get_fid_from_item_list: Callable[[any], str] = self.__set_fid_lookup_fn(scan_options['fid_lookup'])
        # Row results
        self.__fid: str = ''           # Unique id to mark item
        self.__words_amount: int = 0
        self.__items: list[dict[str, any]] = []
        self.__search_words: str = ''  # Words in all items
        self.__context: str = ''       # Context of row (cleared row)

    def fill_row_with_items(self, items: list[dict[str, any]]) -> str:
        """ Put items value in current row fields for translated version """
        assert isinstance(items, list), "items must be a list"
        updated_items: list = []
        for col_n, orig_col_value in enumerate(self.__current_row_items, start=1):
            to_append = orig_col_value
            if col_n in self.__fields:
                for item in items:
                    if item["item_number"] == col_n:
                        unquoted_text = self.__get_unquote_text(orig_col_value)
                        to_append = orig_col_value.replace(unquoted_text, item['text'])
            updated_items.append(to_append)
        return self.__delimiter.join(updated_items)

    @property
    def data(self) -> dict[str, any]:
        """ Return serialized object """
        return {
            'fid': self.__fid,
            'words': self.__words_amount,
            'search_words': self.__search_words.lower(),
            'context': self.__context,
            'items': self.__items,
        }

    @data.setter
    def data(self, row: str):
        """ Set data to serialize """
        self.__current_row_items = row.split(self.__delimiter)
        # Mark data
        self.__fid = self.__get_fid_from_item_list(self.__current_row_items)
        # Null result data
        self.__items = []         # Array of FileMarksObjects
        self.__words_amount = 0   # Words amount in all items
        self.__search_words = ''  # Words in all items
        self.__context = ''       # Context of row (cleared row)

        for col_n, col_value in enumerate(self.__current_row_items, start=1):
            if col_n in self.__fields:
                text = self.__get_unquote_text(col_value)
                clean_text = self.__csv_clean_text(text)
                item_words = self._count_words(clean_text)
                if item_words > 0:
                    self.__words_amount += item_words
                    self.__search_words += f' {clean_text}' if self.__search_words else clean_text   # Add leading space
                    self.__items.append({
                        'item_number': col_n,
                        'md5sum': self._get_md5(col_value.encode(self.__codec)),
                        'md5sum_clear': self._get_md5(clean_text.encode(self.__codec)),
                        'words': item_words,
                        'text': text,
                        'warning': '',
                    })
        if self.__words_amount:
            self.__context = self._clean_text(row)

    def __csv_clean_text(self, text: str) -> str:
        """ Almost BSFG files fix """  # FIXME: Not good way to do methods only for abyss (костыль)
        if text.startswith(r'u,') or text.startswith('a,'):
            return self._clean_text(text[2:-2])  # FIXME  - string len can be 2
        elif text.startswith('[') and text.endswith(']'):
            return self._clean_text(text[1:-1])
        return self._clean_text(text)

    @staticmethod
    def __set_fid_lookup_fn(formula: str) -> Callable[[list[any]], str]:
        """ Work around to get lookup function even if no formula """
        if formula:
            find_unique_id = UniqueIDLookUp()
            find_unique_id.formula = formula
            return find_unique_id.function
        else:
            def blank_function(_) -> str:
                return ''
            return blank_function
