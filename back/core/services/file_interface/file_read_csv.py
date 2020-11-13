from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.id_finder import UniqueIDLookUp
from core.services.file_interface.parser_utils import ParserUtils
from core.services.file_interface.quote_finder import TextQuoteFinder


class LocalizeCSVReader:
    """ Generator class: Read csv file and yield FileMark object to insert in DB """
    def __init__(self, decoded_data, data_codec, scan_options, copy_path=''):
        assert isinstance(decoded_data, str), "Data must be type - string"
        assert isinstance(data_codec, str), "Codec must be type - string"
        self.__data = decoded_data.splitlines()
        self.__row_parser = _MarkDataFromRow(data_codec, scan_options)
        self.__row_index = scan_options['top_rows']
        self.__max_index = len(self.__data) - 1
        # File results
        self.__file_items = 0
        self.__file_words = 0
        # If copy path set - create CCC object to control it
        self.__copy = CopyContextControl(copy_path, data_codec) if copy_path else None

    @property
    def stats(self):
        return self.__file_items, self.__file_words

    def __iter__(self):
        return self

    def __next__(self):
        if self.__row_index > self.__max_index:
            if self.__copy:  # handle copy control
                self.__copy.add_data('')  # To finish file
            raise StopIteration
        if self.__copy:  # handle copy control
            self.__copy.add_data(self.__data[self.__row_index])

        self.__row_parser.data = self.__data[self.__row_index]
        self.__row_index += 1
        if not self.__row_parser.data['words']:
            self.__next__()
        self.__file_items += len(self.__row_parser.data['items'])
        self.__file_words += self.__row_parser.data['words']
        if self.__row_parser.data['fid']:
            return self.__row_parser.data
        else:
            return {**self.__row_parser.data, 'fid': self.__row_index}

    def change_item_content_and_save(self, values: list):
        """ Create row filled with values - to create translation file """
        if self.__copy:  # handle copy control
            to_add = self.__row_parser.fill_row_with_items(values)
            self.__copy.replace_and_save(to_add)


class _MarkDataFromRow(ParserUtils):
    def __init__(self, codec, scan_options):
        self.__current_row_items = []
        # Row parse options
        self.__codec = codec
        self.__delimiter = scan_options['delimiter']
        self.__fields = scan_options['fields']
        # Define function to get text from quoted text
        self.__get_unquote_text = TextQuoteFinder.get_unquoted_text(scan_options['quotes'])
        # Define function to get fID from formula
        self.__get_fid_from_item_list = self.__set_fid_lookup_fn(scan_options['fid_lookup'])
        # Row results
        self.__fid = 0
        self.__words_amount = 0
        self.__items = []
        self.__search_words = ''  # Words in all items
        self.__context = ''       # Context of row (cleared row)

    def fill_row_with_items(self, items: list):
        """ Put items value in current row fields for translated version """
        assert isinstance(items, list), "items must be a list"
        updated_items = []
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
    def data(self):
        return {
            'fid': self.__fid,
            'words': self.__words_amount,
            'items': self.__items,
            'search_words': self.__search_words.lower(),
            'context': self.__context,
        }

    @data.setter
    def data(self, row):
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
                clean_text = self._clean_text(text)
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
                        'warning': None,
                    })
        if self.__words_amount:
            self.__context = self._clean_text(row)

    @staticmethod
    def __set_fid_lookup_fn(formula):
        """ Work around to get lookup function even if no formula """
        if formula:
            find_unique_id = UniqueIDLookUp()
            find_unique_id.formula = formula
            return find_unique_id.function
        else:
            def fun(*args):
                return ''
            return fun
