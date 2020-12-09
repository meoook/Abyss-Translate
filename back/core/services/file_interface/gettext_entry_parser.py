import re

# FIXME: Need to finish comments parsing

# Fixme: Do we really need escape/unescape?


def escape(string_val) -> str:
    """ Escapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in the given string """
    return string_val.replace('\\', r'\\') \
        .replace('\t', r'\t') \
        .replace('\r', r'\r') \
        .replace('\n', r'\n') \
        .replace('\"', r'\"')


def unescape(string_val: str) -> str:
    """ Unescapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in the given string ``string_val`` """
    def unescape_repl(re_exp) -> str:
        char = re_exp.group(1)
        if char == 'n':
            return '\n'
        if char == 't':
            return '\t'
        if char == 'r':
            return '\r'
        if char == '\\':
            return '\\'
        return char  # handles escaped double quote

    return re.sub(r'\\(\\|n|t|r")', unescape_repl, string_val)


class GettextEntrySerializer:
    """ Serializer to parse efficiently and correctly entries for .po file format (gettext) """
    def __init__(self):
        self.__row_type = None  # fid, comment or texts
        # Values can be on several lines. That's why using array to keep them.
        self.__msg_id: list[str] = []         # unique id
        self.__msg_id_plural: list[str] = []  # unique id plural
        self.__msg_c_txt: list[str] = []      # unique id additional data
        self.__comments: list[str] = []       # translator comments for context
        self.__msg_strings: list[str] = []    # texts here
        self.__warning: str = ''              # parse warnings

        self.__types: list[str] = ['msgid', 'msgctxt', 'msgstr', 'msgid_plural']

    @property
    def data(self) -> dict[str, any]:
        return {
            'msgid': ' '.join(self.__msg_id),
            'msgidx': ' '.join(self.__msg_id_plural),
            'msgctxt': ' '.join(self.__msg_c_txt),
            'items': self.__msg_strings,
            'comments': self.__comments,
            'warning': self.__warning
        }

    @data.setter
    def data(self, entry: list[str]):
        """ Set gettext file entry to this function. Entry must be a list of entry rows. """
        self.__parse(entry)

    def __parse(self, entry: list[str]) -> None:
        """ Parse entry row by row and fill entry parameters """
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

    def __added(self, value: str) -> None:
        """ Add value to results by current row type """
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
            self.__comments.append(val)
        elif not self.__warning:
            self.__warning = 'parse error'

    @staticmethod
    def __unquote_and_unescape(value: str) -> str:
        return unescape(value[1:-1]) if value.startswith('"') else unescape(value)
