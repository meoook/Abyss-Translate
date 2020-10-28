import hashlib
import re

WORD_LEN_TO_COUNT = 3
CLEANER_PATTERN = r'[\d\-/\[\]\"\'\\`~.,><:;!?@#$%^&*()+=|_{}]'


class ParserUtils:
    """ Util methods for parser classes """

    @staticmethod
    def _count_words(clean_text):
        """ App function to find number of words(payment) in text """
        return len([x for x in clean_text.split(' ') if len(x) >= WORD_LEN_TO_COUNT])

    @staticmethod
    def _clean_text(text):
        """ Clean text to check if exist and detect language """
        return re.sub(CLEANER_PATTERN, '', text).strip()

    @staticmethod
    def _get_md5(binary_data: bytes):
        return hashlib.md5(binary_data).hexdigest()

    @staticmethod
    def escape(st):   # TODO: Check needed
        """
        Escapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in
        the given string ``st`` and returns it.
        """
        return st.replace('\\', r'\\')\
                 .replace('\t', r'\t')\
                 .replace('\r', r'\r')\
                 .replace('\n', r'\n')\
                 .replace('\"', r'\"')

    @staticmethod
    def unescape(st):   # TODO: Check needed
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
