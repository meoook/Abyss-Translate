import re
import array
import struct
import textwrap

DEFAULT_ENCODING = 'utf-8'
MO_MAGIC = 0x950412de


def wrap(text, width=70, **kwargs):
    """ Wrap a single paragraph of text, returning a list of wrapped lines. """
    return textwrap.wrap(text, width=width, **kwargs)


def escape(st):
    """
    Escapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in
    the given string ``st`` and returns it.
    """
    return st.replace('\\', r'\\') \
        .replace('\t', r'\t') \
        .replace('\r', r'\r') \
        .replace('\n', r'\n') \
        .replace('\"', r'\"')


def unescape(st):
    """
    Unescapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in
    the given string ``st`` and returns it.
    """

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


def natural_sort(lst):
    """ Sort naturally the given list. """
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(lst, key=alphanum_key)


class _BaseFile(list):
    def __init__(self, codec=DEFAULT_ENCODING, wrapwidth=78):
        list.__init__(self)
        self.wrapwidth = wrapwidth
        self.encoding = codec

        self.header = ''
        self.metadata = {}
        self.metadata_is_fuzzy = 0

    def __unicode__(self):
        """ Returns the unicode representation of the file. """
        ret = []
        entries = [self.metadata_as_entry()] + [e for e in self]
        for entry in entries:
            ret.append(entry.__unicode__(self.wrapwidth))
        return '\n'.join(ret)

    def __str__(self):
        return self.__unicode__()

    def __contains__(self, entry):
        return self.find(entry.msg_id, by='msg_id', msgctxt=entry.msg_c_txt) is not None

    def __eq__(self, other):
        return str(self) == str(other)

    def append(self, entry):
        super(_BaseFile, self).append(entry)

    def insert(self, index, entry):
        super(_BaseFile, self).insert(index, entry)

    def metadata_as_entry(self):
        """ Returns the file metadata as a :class:`~polib.POFile` instance. """
        e = POEntry(msgid='')
        mdata = self.ordered_metadata()
        if mdata:
            strs = []
            for name, value in mdata:
                # Strip whitespace off each line in a multi-line entry
                strs.append('%s: %s' % (name, value))
            e.msgstr = '\n'.join(strs) + '\n'
        if self.metadata_is_fuzzy:
            e.flags.append('fuzzy')
        return e

    def find(self, st, by='msg_id', msgctxt=False):
        """ Find the entry which msg_id (or property identified by the ``by`` argument) matches the string ``st`` """
        entries = self[:]

        matches = []
        for e in entries:
            if getattr(e, by) == st:
                if msgctxt and e.msgctxt != msgctxt:
                    continue
                matches.append(e)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            if not msgctxt:
                # find the entry with no msgctx
                e = None
                for m in matches:
                    if not m.msgctxt:
                        e = m
                if e:
                    return e
                # fallback to the first entry found
                return matches[0]
        return None

    def ordered_metadata(self):
        """
        Convenience method that returns an ordered version of the metadata
        dictionary. The return value is list of tuples (metadata name,
        metadata_value).
        """
        # copy the dict first
        metadata = self.metadata.copy()
        data_order = [
            'Project-Id-Version',
            'Report-Msgid-Bugs-To',
            'POT-Creation-Date',
            'PO-Revision-Date',
            'Last-Translator',
            'Language-Team',
            'Language',
            'MIME-Version',
            'Content-Type',
            'Content-Transfer-Encoding',
            'Plural-Forms'
        ]
        ordered_data = []
        for data in data_order:
            try:
                value = metadata.pop(data)
                ordered_data.append((data, value))
            except KeyError:
                pass
        # the rest of the metadata will be alphabetically ordered since there are no specs for this AFAIK
        for data in natural_sort(metadata.keys()):
            value = metadata[data]
            ordered_data.append((data, value))
        return ordered_data

    def to_binary(self):
        """ Return the binary representation of the file """
        offsets = []
        entries = self

        # add metadata entry
        entries.sort(key=lambda o: o.msg_id_with_context.encode('utf-8'))
        m_entry = self.metadata_as_entry()
        entries = [m_entry] + entries
        entries_len = len(entries)
        ids, binary_strings = b'', b''
        for e in entries:
            # For each string, we need size and file offset.  Each string is
            # NUL terminated; the NUL does not count into the size.
            msg_id = b''
            if e.msg_c_txt:
                # Contexts are stored by storing the concatenation of the
                # context, a <EOT> byte, and the original string
                msg_id = self._encode(e.msg_c_txt + '\4')
            if e.msg_id_plural:
                msgstr = []
                for index in sorted(e.msgstr_plural.keys()):
                    msgstr.append(e.msgstr_plural[index])
                msg_id += self._encode(e.msg_id + '\0' + e.msg_id_plural)
                msgstr = self._encode('\0'.join(msgstr))
            else:
                msg_id += self._encode(e.msg_id)
                msgstr = self._encode(e.msgstr)
            offsets.append((len(ids), len(msg_id), len(binary_strings), len(msgstr)))
            ids += msg_id + b'\0'
            binary_strings += msgstr + b'\0'

        # The header is 7 32-bit unsigned integers.
        key_start = 7 * 4 + 16 * entries_len
        # and the values start after the keys
        value_start = key_start + len(ids)
        k_offsets = []
        v_offsets = []
        # The string table first has the list of keys, then the list of values.
        # Each entry has first the size of the string, then the file offset.
        for o1, l1, o2, l2 in offsets:
            k_offsets += [l1, o1 + key_start]
            v_offsets += [l2, o2 + value_start]
        offsets = k_offsets + v_offsets

        output = struct.pack("Iiiiiii", MO_MAGIC, 0, entries_len, 7 * 4,  7 * 4 + entries_len * 8, 0, key_start)
        output += array.array("i", offsets).tobytes()
        output += ids
        output += binary_strings
        return output

    def _encode(self, mixed):
        """  Encodes the given ``mixed`` argument with the file encoding and returns the encoded string """
        if isinstance(mixed, str):
            mixed = mixed.encode(self.encoding)
        return mixed


class _BaseEntry(object):
    def __init__(self, *args, **kwargs):
        self.msg_id = kwargs.get('msg_id', '')
        self.msgstr = kwargs.get('msgstr', '')
        self.msg_id_plural = kwargs.get('msg_id_plural', '')
        self.msgstr_plural = kwargs.get('msgstr_plural', {})
        self.msg_c_txt = kwargs.get('msg_c_txt', None)
        self.encoding = kwargs.get('encoding', DEFAULT_ENCODING)

    def __unicode__(self, wrap_width=78):
        """ To write file """
        del_flag = ''
        ret = []
        # write the msg_c_txt if any
        if self.msg_c_txt:
            ret += self._str_field("msg_c_txt", del_flag, "", self.msg_c_txt, wrap_width)
        # write the msg_id
        ret += self._str_field("msg_id", del_flag, "", self.msg_id, wrap_width)
        # write the msg_id_plural if any
        if self.msg_id_plural:
            ret += self._str_field("msg_id_plural", del_flag, "", self.msg_id_plural, wrap_width)
        if self.msgstr_plural:
            # write the msg_str_plural if any
            msg_strings = self.msgstr_plural
            keys = list(msg_strings)
            keys.sort()
            for index in keys:
                msg_str = msg_strings[index]
                plural_index = '[%s]' % index
                ret += self._str_field("msg_str", del_flag, plural_index, msg_str, wrap_width)
        else:
            # otherwise write the msg_str
            ret += self._str_field("msg_str", del_flag, "", self.msgstr, wrap_width)
        ret.append('')
        ret = '\n'.join(ret)
        return ret

    def __str__(self):
        return self.__unicode__()

    @staticmethod
    def _str_field(field_name, del_flag, plural_index, field, wrap_width=78):
        lines = field.splitlines(True)
        if len(lines) > 1:
            lines = [''] + lines  # start with initial empty line
        else:
            escaped_field = escape(field)
            special_chars_count = 0
            for c in ['\\', '\n', '\r', '\t', '"']:
                special_chars_count += field.count(c)
            # comparison must take into account field_name length + one space + 2 quotes (eg. msg_id "<string>")
            f_length = len(field_name) + 3
            if plural_index:
                f_length += len(plural_index)
            real_wrap_width = wrap_width - f_length + special_chars_count
            if wrap_width > 0 and len(field) > real_wrap_width:
                # Wrap the line but take field name into account
                lines = [''] + [unescape(item) for item in wrap(
                    escaped_field,
                    wrap_width - 2,  # 2 for quotes ""
                    drop_whitespace=False,
                    break_long_words=False
                )]
            else:
                lines = [field]
        if field_name.startswith('previous_'):
            # quick and dirty trick to get the real field name
            field_name = field_name[9:]

        ret = ['%s%s%s "%s"' % (del_flag, field_name, plural_index, escape(lines.pop(0)))]
        for line in lines:
            ret.append('%s"%s"' % (del_flag, escape(line)))
        return ret


class POEntry(_BaseEntry):
    """ Represents a po file entry. """

    def __init__(self, *args, **kwargs):
        _BaseEntry.__init__(self, *args, **kwargs)
        self.comment = kwargs.get('comment', '')
        self.t_comment = kwargs.get('t_comment', '')
        self.occurrences = kwargs.get('occurrences', [])
        self.flags = kwargs.get('flags', [])
        self.previous_msg_c_txt = kwargs.get('previous_msg_c_txt', None)
        self.previous_msg_id = kwargs.get('previous_msg_id', None)
        self.previous_msg_id_plural = kwargs.get('previous_msg_id_plural', None)
        self.line_num = kwargs.get('line_num', None)

    def __unicode__(self, wrap_width=78):
        """ Returns the unicode representation of the entry. """
        ret = []
        # comments first, if any (with text wrapping as xgettext does)
        comments = [('comment', '#. '), ('t_comment', '# ')]
        for c in comments:
            val = getattr(self, c[0])
            if val:
                for comment in val.split('\n'):
                    if 0 < wrap_width < len(comment) + len(c[1]):
                        ret += wrap(
                            comment,
                            wrap_width,
                            initial_indent=c[1],
                            subsequent_indent=c[1],
                            break_long_words=False
                        )
                    else:
                        ret.append('%s%s' % (c[1], comment))

        # occurrences (with text wrapping as x_gettext does)
        if self.occurrences:
            file_list = []
            for f_path, line_no in self.occurrences:
                if line_no:
                    file_list.append('%s:%s' % (f_path, line_no))
                else:
                    file_list.append(f_path)
            file_str = ' '.join(file_list)
            if 0 < wrap_width < len(file_str) + 3:
                ret += [_line.replace('*', '-') for _line in wrap(
                    file_str.replace('-', '*'),
                    wrap_width,
                    initial_indent='#: ',
                    subsequent_indent='#: ',
                    break_long_words=False
                )]
            else:
                ret.append('#: ' + file_str)

        if self.flags:
            ret.append('#, %s' % ', '.join(self.flags))

        # previous context and previous msg_id/msg_id_plural
        fields = ['previous_msg_c_txt', 'previous_msg_id', 'previous_msg_id_plural']

        prefix = "#| "
        for f in fields:
            val = getattr(self, f)
            if val:
                ret += self._str_field(f, prefix, "", val, wrap_width)

        ret.append(_BaseEntry.__unicode__(self, wrap_width))
        ret = '\n'.join(ret)
        return ret

    @property
    def msg_id_with_context(self):
        if self.msg_c_txt:
            return '%s%s%s' % (self.msg_c_txt, "\x04", self.msg_id)
        return self.msg_id

    def __hash__(self):
        return hash((self.msg_id, self.msgstr))


class _POFileParser:
    """ A finite state machine to parse efficiently and correctly po file format. """
    def __init__(self, codec, data: list):
        self.__data = data
        self.transitions = {}
        self.current_entry = POEntry()
        self.current_state = 'st'
        self.current_token = None
        # two memo flags used in handlers
        self.msg_str_index = 0
        self.entry_obsolete = 0
        # Configure the state machine, by adding transitions.
        # Signification of symbols:
        #     * ST: Beginning of the file (start)
        #     * HE: Header
        #     * TC: a translation comment
        #     * GC: a generated comment
        #     * OC: a file/line occurrence
        #     * FL: a flags line
        #     * CT: a message context
        #     * PC: a previous msg_c_txt
        #     * PM: a previous msg_id
        #     * PP: a previous msg_id_plural
        #     * MI: a msg_id
        #     * MP: a msg_id plural
        #     * MS: a msgstr
        #     * MX: a msgstr plural
        #     * MC: a msg_id or msgstr continuation line
        all_short_cats = ['st', 'he', 'gc', 'oc', 'fl', 'ct', 'pc', 'pm', 'pp', 'tc', 'ms', 'mp', 'mx', 'mi']

        self.add('tc', ['st', 'he'],                                     'he')
        self.add('tc', ['gc', 'oc', 'fl', 'tc', 'pc', 'pm', 'pp', 'ms',
                        'mp', 'mx', 'mi'],                               'tc')
        self.add('gc', all_short_cats,                                   'gc')
        self.add('oc', all_short_cats,                                   'oc')
        self.add('fl', all_short_cats,                                   'fl')
        self.add('pc', all_short_cats,                                   'pc')
        self.add('pm', all_short_cats,                                   'pm')
        self.add('pp', all_short_cats,                                   'pp')
        self.add('ct', ['st', 'he', 'gc', 'oc', 'fl', 'tc', 'pc', 'pm',
                        'pp', 'ms', 'mx'],                               'ct')
        self.add('mi', ['st', 'he', 'gc', 'oc', 'fl', 'ct', 'tc', 'pc',
                 'pm', 'pp', 'ms', 'mx'],                                'mi')
        self.add('mp', ['tc', 'gc', 'pc', 'pm', 'pp', 'mi'],             'mp')
        self.add('ms', ['mi', 'mp', 'tc'],                               'ms')
        self.add('mx', ['mi', 'mx', 'mp', 'tc'],                         'mx')
        self.add('mc', ['ct', 'mi', 'mp', 'ms', 'mx', 'pm', 'pp', 'pc'], 'mc')

    def parse(self):
        """ Run the state machine, parse the file line by line and call process() with the current matched symbol """

        keywords = {
            'msgctxt': 'ct',
            'msgid': 'mi',
            'msgstr': 'ms',
            'msgid_plural': 'mp',
        }
        prev_keywords = {
            'msgid_plural': 'pp',
            'msgid': 'pm',
            'msgctxt': 'pc',
        }
        tokens = []
        for line in self.__data:
            line = line.strip()
            if line == '':
                continue

            tokens = line.split(None, 2)
            nb_tokens = len(tokens)

            if tokens[0] == '#~|':
                continue

            if tokens[0] == '#~' and nb_tokens > 1:
                line = line[3:].strip()
                tokens = tokens[1:]
                nb_tokens -= 1
                self.entry_obsolete = 1
            else:
                self.entry_obsolete = 0

            # Take care of keywords like msg_id, msg_id_plural, msg_c_txt & msgstr.
            if tokens[0] in keywords and nb_tokens > 1:
                line = line[len(tokens[0]):].lstrip()
                if re.search(r'([^\\]|^)"', line[1:-1]):
                    raise IOError('Syntax error (line %s): unescaped double quote found' % self.current_line)
                self.current_token = line
                self.process(keywords[tokens[0]])
                continue

            self.current_token = line

            if tokens[0] == '#:':
                if nb_tokens <= 1:  # empty ?
                    continue
                # we are on a occurrences line
                self.process('oc')

            elif line[:1] == '"':
                # we are on a continuation line
                if re.search(r'([^\\]|^)"', line[1:-1]):
                    raise IOError('Syntax error (line %s): unescaped double quote found' % self.current_line)
                self.process('mc')

            elif line[:7] == 'msgstr[':
                # we are on a msgstr plural
                self.process('mx')

            elif tokens[0] == '#,':
                if nb_tokens <= 1:
                    continue
                # we are on a flags line
                self.process('fl')

            elif tokens[0] == '#' or tokens[0].startswith('##'):
                if line == '#':
                    line += ' '
                # we are on a translator comment line
                self.process('tc')

            elif tokens[0] == '#.':
                if nb_tokens <= 1:
                    continue
                # we are on a generated comment line
                self.process('gc')

            elif tokens[0] == '#|':
                if nb_tokens <= 1:
                    raise IOError('Syntax error in po file (line %s)' % self.current_line)

                # Remove the marker and any whitespace right after that.
                line = line[2:].lstrip()
                self.current_token = line

                if tokens[1].startswith('"'):
                    # Continuation of previous metadata.
                    self.process('mc')
                    continue

                if nb_tokens == 2:
                    # Invalid continuation line.
                    raise IOError('Syntax error (line %s): invalid continuation line' % self.current_line)

                # we are on a "previous translation" comment line,
                if tokens[1] not in prev_keywords:
                    # Unknown keyword in previous translation comment.
                    raise IOError('Syntax error (line %s): unknown keyword %s' % (self.current_line, tokens[1]))

                # Remove the keyword and any whitespace
                # between it and the starting quote.
                line = line[len(tokens[1]):].lstrip()
                self.current_token = line
                self.process(prev_keywords[tokens[1]])

            else:
                raise IOError('Syntax error in po file (line %s)' % self.current_line)

        if self.current_entry and len(tokens) > 0 and not tokens[0].startswith('#'):
            self.instance.append(self.current_entry)

        # before returning the instance, check if there's metadata and if so extract it in a dict
        meta_data_entry = self.instance.find('')
        if meta_data_entry:  # metadata found
            # remove the entry
            self.instance.remove(meta_data_entry)
            self.instance.metadata_is_fuzzy = meta_data_entry.flags
            key = None
            for msg in meta_data_entry.msgstr.splitlines():
                try:
                    key, val = msg.split(':', 1)
                    self.instance.metadata[key] = val.strip()
                except (ValueError, KeyError):
                    if key is not None:
                        self.instance.metadata[key] += '\n' + msg.strip()
        # close opened file
        if not isinstance(self.__data, list):  # must be file
            self.__data.close()
        return self.instance

    def add(self, symbol, states, next_state):
        """ Add a transition to the state machine """
        for state in states:
            action = getattr(self, 'handle_%s' % next_state)
            self.transitions[(symbol, state)] = (action, next_state)

    def process(self, symbol):
        """ Process the transition corresponding to the current state and the symbol provided """
        try:
            (action, state) = self.transitions[(symbol, self.current_state)]
            if action():
                self.current_state = state
        except Exception:
            raise IOError('Syntax error in po file (line %s)' % self.current_line)

    # state handlers

    def handle_he(self):
        """Handle a header comment """
        if self.instance.header != '':
            self.instance.header += '\n'
        self.instance.header += self.current_token[2:]
        return 1

    def handle_tc(self):
        """Handle a translator comment """
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        if self.current_entry.t_comment != '':
            self.current_entry.t_comment += '\n'
        tcomment = self.current_token.lstrip('#')
        if tcomment.startswith(' '):
            tcomment = tcomment[1:]
        self.current_entry.t_comment += tcomment
        return True

    def handle_gc(self):
        """Handle a generated comment."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        if self.current_entry.comment != '':
            self.current_entry.comment += '\n'
        self.current_entry.comment += self.current_token[3:]
        return True

    def handle_oc(self):
        """Handle a file:num occurrence."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        occurrences = self.current_token[3:].split()
        for occurrence in occurrences:
            if occurrence != '':
                try:
                    fil, line = occurrence.rsplit(':', 1)
                    if not line.isdigit():
                        fil = occurrence
                        line = ''
                    self.current_entry.occurrences.append((fil, line))
                except (ValueError, AttributeError):
                    self.current_entry.occurrences.append((occurrence, ''))
        return True

    def handle_fl(self):
        """Handle a flags line."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.flags += [c.strip() for c in self.current_token[3:].split(',')]
        return True

    def handle_pp(self):
        """Handle a previous msg_id_plural line."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.previous_msg_id_plural = \
            unescape(self.current_token[1:-1])
        return True

    def handle_pm(self):
        """Handle a previous msg_id line."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.previous_msg_id = \
            unescape(self.current_token[1:-1])
        return True

    def handle_pc(self):
        """Handle a previous msg_c_txt line."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.previous_msg_c_txt = \
            unescape(self.current_token[1:-1])
        return True

    def handle_ct(self):
        """Handle a msg_c_txt."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.msg_c_txt = unescape(self.current_token[1:-1])
        return True

    def handle_mi(self):
        """Handle a msg_id."""
        if self.current_state in ['mc', 'ms', 'mx']:
            self.instance.append(self.current_entry)
            self.current_entry = POEntry(linenum=self.current_line)
        self.current_entry.obsolete = self.entry_obsolete
        self.current_entry.msg_id = unescape(self.current_token[1:-1])
        return True

    def handle_mp(self):
        """Handle a msg_id plural."""
        self.current_entry.msg_id_plural = unescape(self.current_token[1:-1])
        return True

    def handle_ms(self):
        """Handle a msgstr."""
        self.current_entry.msgstr = unescape(self.current_token[1:-1])
        return True

    def handle_mx(self):
        """Handle a msgstr plural."""
        index = self.current_token[7]
        value = self.current_token[self.current_token.find('"') + 1:-1]
        self.current_entry.msgstr_plural[int(index)] = unescape(value)
        self.msg_str_index = int(index)
        return True

    def handle_mc(self):
        """Handle a msg_id or msgstr continuation line."""
        token = unescape(self.current_token[1:-1])
        if self.current_state == 'ct':
            self.current_entry.msg_c_txt += token
        elif self.current_state == 'mi':
            self.current_entry.msg_id += token
        elif self.current_state == 'mp':
            self.current_entry.msg_id_plural += token
        elif self.current_state == 'ms':
            self.current_entry.msgstr += token
        elif self.current_state == 'mx':
            self.current_entry.msgstr_plural[self.msg_str_index] += token
        elif self.current_state == 'pp':
            self.current_entry.previous_msg_id_plural += token
        elif self.current_state == 'pm':
            self.current_entry.previous_msg_id += token
        elif self.current_state == 'pc':
            self.current_entry.previous_msg_c_txt += token
        # don't change the current state
        return False


