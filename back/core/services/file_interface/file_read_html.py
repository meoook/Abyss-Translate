from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.html_parser import HtmlContextParser
from core.services.file_interface.parser_utils import ParserUtils

# regular = r'<([\w]+)(\s.*)?>\s*([^<>]+[^\s])\s*<'
# regggaa = r'<([\w]+)([^>]*)?>(\s*.*)</\1>'
#
# ONE_CONTENT_LOOK_UP = r'<([\w]+)([^>]*)?>([^\0]+)</\1>'
# xx = '(?:</\w+>|^)([^><]+)<'


class LocalizeHtmlReader(ParserUtils):
    """ Read html file and yield FileMark object to insert in DB. Also control creating translation copy. """
    def __init__(self, decoded_data: str, data_codec: str, _, copy_path: str = ''):
        self.__codec: str = data_codec
        _html_parser = HtmlContextParser(decoded_data)  # Parse html data to list of elements
        self.__data: list[dict[str, str]] = _html_parser.data
        self.__elem_index: int = 0
        self.__eof_index: int = len(self.__data) - 1
        # File results
        self.__file_items: int = 0
        self.__file_words: int = 0
        # If copy path set - create CCC object to control copy creation
        self.__copy = CopyContextControl(copy_path, data_codec, mode='append') if copy_path else None

    @property
    def stats(self) -> tuple[int, int]:
        return self.__file_items, self.__file_words

    def __iter__(self):
        return self

    def __next__(self) -> dict[str, any]:
        if self.__elem_index >= self.__eof_index:
            if self.__copy:  # handle copy control
                _html_left_data = self.__data[self.__eof_index]
                self.__copy.add_data(_html_left_data['prefix'])
                self.__copy.finish()  # To finish file
            raise StopIteration
        # Set next element
        _html_item = self.__data[self.__elem_index]
        self.__elem_index += 1

        if self.__copy:  # handle copy control
            self.__copy.add_data(_html_item['prefix'])
            self.__copy.add_data(_html_item['text'])

        text: str = _html_item['text']
        clean_text: str = self._clean_text(text)
        item_words: int = self._count_words(clean_text)

        if not item_words:  # Pass if no words in text
            self.__next__()

        self.__file_items += 1  # only one item for html
        self.__file_words += item_words

        return self.__serialize(text, clean_text, item_words, _html_item)

    def __serialize(self, text: str, clean_text: str, words: int, html_item: dict[str, str]) -> dict[str, any]:
        _item = {
                'item_number': 1,
                'md5sum': self._get_md5(text.encode(self.__codec)),
                'md5sum_clear': self._get_md5(clean_text.encode(self.__codec)),
                'words': words,
                'text': text,
                'warning': html_item['warning'],
            }
        return {
            'fid': self.__elem_dom_fix_fix_len(html_item['dom']),
            'words': words,
            'search_words': clean_text.lower(),
            'context': html_item['prefix'] + html_item['text'],
            'items': [_item, ],
        }

    def __elem_dom_fix_fix_len(self, string_dom: str) -> str:
        """ Fix len of element dom tree to 255 symbols (DB indexed) """
        if len(string_dom) < 255:
            return string_dom
        _without_dots = string_dom.replace(':', '')
        if len(_without_dots) < 255:
            return _without_dots
        _binary = _without_dots.encode(self.__codec)
        return self._get_md5(_binary)

    def copy_write_mark_items(self, values: list[dict[str, any]]) -> None:
        """ Translation file copy write new translates for current item """
        if self.__copy and values:  # handle copy control
            to_add = values[0]['text']
            self.__copy.replace_and_save(to_add)
