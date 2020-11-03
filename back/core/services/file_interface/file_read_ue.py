import re

from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.parser_utils import ParserUtils

# FIXME: make class more friendly


def escape(st):
    """ Escapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in the given string """
    return st.replace('\\', r'\\') \
        .replace('\t', r'\t') \
        .replace('\r', r'\r') \
        .replace('\n', r'\n') \
        .replace('\"', r'\"')


def unescape(st):
    """ Unescapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in the given string ``st`` """
    def unescape_repl(m):
        m = m.group(1)
        if m == 'n':
            return '\n'
        if m == 't':
            return '\t'
        if m == 'r':
            return '\r'
        if m == '\\':
            return '\\'
        return m  # handles escaped double quote

    return re.sub(r'\\(\\|n|t|r")', unescape_repl, st)


class LocalizeUEReader:
    """ Generator class: Read csv file and yield FileMark object to insert in DB """
    def __init__(self, decoded_data, data_codec, scan_options, copy_path=''):
        assert isinstance(decoded_data, str), "Data must be type - string"
        assert isinstance(data_codec, str), "Codec must be type - string"
        self.__data = decoded_data.splitlines()
        # self.__data = decoded_data.split('\n')  # Don't use splitlines - cos it cuts \r
        self.__parser = _MarkDataFromUE(data_codec, scan_options)  # Codec needed for md5
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
        self.__parser.data = self.__next_entry()
        if not self.__parser.data['words']:
            self.__next__()
        self.__file_items += len(self.__parser.data['items'])
        self.__file_words += self.__parser.data['words']
        self.__row_index += 1
        return self.__parser.data if self.__parser.data['fid'] else {**self.__parser.data, 'fid': self.__row_index}

    def __next_entry(self):
        """ Return entry or empty array if EOF """
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
                elif not po_entry:  # Empty row - means end of po_entry
                    po_entry.append(row)  # Append first empty row too
                else:
                    entry_not_finished = False
        if self.__copy:  # handle copy control
            self.__copy.add_data('\n'.join(po_entry))
        return po_entry

    def change_item_content_and_save(self, values: list):
        """ Create row filled with values - to create translation file """
        if self.__copy:  # handle copy control
            to_add = self.__parser.fill_entry_with_items(values)
            self.__copy.add_data('\n'.join(to_add))


class _MarkDataFromUE(ParserUtils):
    def __init__(self, codec, scan_options):
        self.__current_items = []
        # Row parse options
        self.__codec = codec
        # Define function to get fID from formula
        self.__get_fid_from_entry = self.__fid_lookup(scan_options['fid_lookup'])
        # Row results
        self.__fid = 0
        self.__words_amount = 0
        self.__items = []
        self.__search_words = ''  # Words in all items
        self.__context = ''       # Context of row (cleared row)

    def fill_entry_with_items(self, items: list):
        """ Put items value in current row fields for translated version """
        assert isinstance(items, list), "items must be a list"
        updated_items = []
        msg_id_idx = 1
        for orig_row_value in self.__current_items:
            to_append = orig_row_value
            finder = re.search(r'^.*msgid[^"]+"(.*)"', orig_row_value)
            if finder:  # must be in first chars
                for item in items:
                    if item["item_number"] == msg_id_idx:
                        to_append = orig_row_value.replace(finder.group(1), item['text'])
            updated_items.append(to_append)
        return updated_items

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
    def data(self, entry: list):
        self.__current_items = entry

        entry_parser = _PoEntryParser()
        entry_parser.data = entry

        # Null result data
        self.__items = []         # Array of FileMarksObjects
        self.__words_amount = 0   # Words amount in all items
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

    def __fid_lookup(self, formula):
        get_md5 = self._get_md5
        codec = self.__codec

        def entry_hash(msg_id, msg_c_txt):
            if formula == '1':    # msgid only
                return get_md5(msg_id.encode(codec))
            elif formula == '2':  # msgid + msgctxt
                return get_md5(f'{msg_id}{msg_c_txt}'.encode(codec))
            else:                 # no fid
                return ''

        return entry_hash


class _PoEntryParser:
    """ Machine to parse efficiently and correctly entries for PO file format """
    def __init__(self):
        self.__row_type = None  # fid, comment or texts
        self.__msg_id = []  # for fid and context
        self.__msg_id_plural = []  # for fid and context
        self.__msg_c_txt = []  # for fid and context
        self.__comments = ''  # translator comments for context
        self.__msg_strings = []  # texts here
        self.__warning = ''  # parse warnings

        self.__types = ['msgid', 'msgctxt', 'msgstr', 'msgid_plural']

    @property
    def data(self):
        return {
            'msgid': ' '.join(self.__msg_id),
            'msgidx': ' '.join(self.__msg_id_plural),
            'msgctxt': ' '.join(self.__msg_c_txt),
            'items': self.__msg_strings,
            'comments': self.__comments,
            'warning': self.__warning
        }

    @data.setter
    def data(self, entry):
        self.__parse(entry)

    def __parse(self, entry):
        """ Run the state machine, parse the file line by line and call process() with the current matched symbol """
        for entry_line in entry:
            entry_line = entry_line.strip()
            if not entry_line:
                continue

            if entry_line[:1] == '"':
                # we are on a continuation line (adder)
                if not self.__row_type:
                    self.__warning = 'Syntax error: unknown comment or add line'
                elif re.search(r'([^\\]|^)"', entry_line[1:-1]):
                    self.__warning = 'Syntax error: unescaped double quote found'
                else:
                    value = unescape(entry_line[1:-1]).strip()  # unquote
                    if value:
                        self.__added(value)
                continue
            self.__row_type = None

            row_items = entry_line.split(None, 2)
            items_amount = len(row_items)

            if row_items[0] == '#~|':
                continue
            if row_items[0] in ['#~', '#|']:   # Cutter
                # Remove the marker and any whitespace
                entry_line = entry_line[3:].strip()  # TODO: mb [4:-1]
                row_items = row_items[1:]
                items_amount -= 1
            if items_amount < 2 or not row_items[1]:
                continue

            if row_items[0] in self.__types:
                # Add like msg_id, msg_id_plural, msg_c_txt & msgstr.
                offset = len(row_items[0])
                entry_line = entry_line[offset:].lstrip()
                if re.search(r'([^\\]|^)"', entry_line[1:-1]):
                    self.__warning = 'Syntax error: unescaped double quote found'
                else:
                    self.__row_type = row_items[0]
                    self.__added(entry_line)
            elif entry_line[:7] == 'msgstr[':
                # we are on a msgstr plural
                self.__row_type = 'msgstr'
                self.__added(row_items[1])
            elif row_items[0] == '#' or row_items[0].startswith('##'):
                # we are on a translator comment line
                self.__row_type = 'comments'
                self.__added(row_items[1])
            elif row_items[0] == '#:':
                # we are on reference line
                pass
            elif row_items[0] == '#,':
                # we are on a flags line
                pass
            elif row_items[0] == '#.':
                # we are on a generated/extracted comment line
                pass
            else:
                self.__warning = 'Syntax error'

    def __added(self, value):
        val = self.__unquote_and_unescape(value)
        if not val:
            return
        elif self.__row_type == 'msgid':
            self.__msg_id.append(val)
        elif self.__row_type == 'msgctxt':
            self.__msg_c_txt.append(val)
        elif self.__row_type == 'msgstr':
            self.__msg_strings.append(val)
        elif self.__row_type == 'msgid_plural':
            self.__msg_id_plural.append(val)
        elif self.__row_type == 'comments':
            self.__comments = f'{self.__comments} {val}' if self.__comments else val
        elif not self.__warning:
            self.__warning = 'parse error'

    @staticmethod
    def __unquote_and_unescape(value):
        return unescape(value[1:-1]) if value.startswith('"') else unescape(value)
