import re
from typing import Callable

from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.gettext_entry_parser import GettextEntrySerializer
from core.services.file_interface.parser_utils import ParserUtils


class LocalizeUEReader:
    """ Read gettext (.po) file and yield FileMark object to insert in DB. Also control creating translation copy. """

    def __init__(self, decoded_data: str, data_codec: str, scan_options: dict[str, any], copy_path: str = ''):
        self.__data: list[str] = decoded_data.splitlines()
        # FIXME: self.__data = decoded_data.split('\n')  # Don't use splitlines - cos it cuts \r
        self.__parser = _GettextToMarkSerializer(data_codec, scan_options)  # Codec needed for md5
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
        if self.__row_index > self.__max_index:
            if self.__copy:  # handle copy control
                self.__copy.finish()  # To finish file
            raise StopIteration
        self.__parser.data = self.__next_entry()  # Copy control here
        if not self.__parser.data['words']:
            self.__next__()
        self.__file_items += len(self.__parser.data['items'])
        self.__file_words += self.__parser.data['words']
        return self.__parser.data if self.__parser.data['fid'] else {**self.__parser.data, 'fid': self.__row_index}

    def __next_entry(self) -> list[str]:
        """ Return array of entry rows """
        po_entry = []
        entry_not_finished = True
        while entry_not_finished:
            try:
                row = self.__data[self.__row_index]
            except IndexError:
                entry_not_finished = False
            else:
                self.__row_index += 1
                if row.strip():
                    po_entry.append(row)
                elif not po_entry:  # Empty row - means end of entry
                    po_entry.append(row)  # Add first empty row as start of entry
                else:
                    entry_not_finished = False
        if self.__copy:  # handle copy control
            self.__copy.add_data('\n'.join(po_entry))
        return po_entry

    def copy_write_mark_items(self, values: list[dict[str, any]]) -> None:
        """ Translation file copy write new translates for current item """
        if self.__copy:  # handle copy control
            to_add = self.__parser.fill_entry_with_values(values)
            self.__copy.add_data('\n'.join(to_add))


class _GettextToMarkSerializer(ParserUtils):
    def __init__(self, codec: str, scan_options: dict[str, any]):
        self.__current_items: list[str] = []
        # Row parse options
        self.__codec = codec
        # Define function to get fID from formula
        self.__get_fid_from_entry = self.__fid_lookup_function_by_formula(scan_options['fid_lookup'])
        # Row results
        self.__fid: str = ''           # Unique id to mark item
        self.__words_amount: int = 0
        self.__items: list[dict[str, any]] = []
        self.__search_words: str = ''  # Words in all items
        self.__context: str = ''       # Context of row (cleared row)

    def fill_entry_with_values(self, new_values: list[dict[str, any]]) -> list[str]:
        """ Put items value in current entry for translated version """
        assert isinstance(new_values, list), "items must be a list"
        sorted_values = sorted(new_values, key=lambda obj: obj['item_number'])
        updated_items = []
        msg_id_index = 1  # FIXME: test this
        for orig_row_value in self.__current_items:
            to_append = orig_row_value
            finder = re.search(r'^.*msgid[^"]+"(.*)"', orig_row_value)
            if finder:  # must be in first chars
                for item in sorted_values:
                    if item["item_number"] == msg_id_index:
                        msg_id_index += 1  # FIXME: test this
                        to_append = orig_row_value.replace(finder.group(1), item['text'])
            updated_items.append(to_append)
        return updated_items

    @property
    def data(self) -> dict[str, any]:
        return {
            'fid': self.__fid,
            'words': self.__words_amount,
            'items': self.__items,
            'search_words': self.__search_words.lower(),
            'context': self.__context,
        }

    @data.setter
    def data(self, entry: list[str]):
        self.__current_items = entry

        entry_parser = GettextEntrySerializer()
        entry_parser.data = entry

        # Null result data
        self.__items = []  # Array of FileMarksObjects
        self.__words_amount = 0  # Words amount in all items
        self.__search_words = ''  # Words in all items

        for item_number, item_text in enumerate(entry_parser.data['items'], start=1):
            clean_text = self._clean_text(item_text)
            item_words = self._count_words(clean_text)
            if item_words > 0:
                self.__words_amount += item_words
                self.__search_words += f' {clean_text}' if self.__search_words else clean_text  # Add leading space
                self.__items.append({
                    'item_number': item_number,
                    'md5sum': self._get_md5(item_text.encode(self.__codec)),
                    'md5sum_clear': self._get_md5(clean_text.encode(self.__codec)),
                    'words': item_words,
                    'text': item_text,
                    'warning': entry_parser.data['warning'],
                })

        context = []
        if entry_parser.data['comments']:
            context.append(entry_parser.data['comments'])
        if entry_parser.data['msgidx']:  # If plural set - use it as context
            context.append(entry_parser.data['msgidx'])
        else:  # Then use id fields as context
            context.append(entry_parser.data['msgid'])

        # Mark data
        self.__context = '\n'.join(context)  # Context of entry (not cleared for UE)
        self.__fid = self.__get_fid_from_entry(entry_parser.data['msgid'], entry_parser.data['msgctxt'])

    def __fid_lookup_function_by_formula(self, formula: str) -> Callable[[str, str], str]:
        """ Return function to find FID """
        get_md5 = self._get_md5
        codec = self.__codec

        def entry_hash(msg_id: str, msg_c_txt: str) -> str:
            if formula == '1':  # msgid only
                return get_md5(msg_id.encode(codec))
            elif formula == '2':  # msgid + msgctxt
                return get_md5(f'{msg_id}{msg_c_txt}'.encode(codec))
            else:  # no fid if formula not set
                return ''

        return entry_hash
