import hashlib
import re
from django.conf import settings

# WORD_LEN_TO_COUNT = 3
CLEANER_PATTERN = r'[\r\d\-/\[\]\"\'\\`~.,><:;!?@#$%^&*()+=|_{}]'


class ParserUtils:
    """ Util methods for parser classes """

    @staticmethod
    def _count_words(clean_text: str) -> int:
        """ App function to find number of words(payment) in text """
        return len([x for x in clean_text.split(' ') if len(x) >= settings.WORD_LEN_TO_COUNT])
        # return len([x for x in clean_text.split(' ') if len(x) >= WORD_LEN_TO_COUNT])

    @staticmethod
    def _clean_text(text: str) -> str:
        """ Clean text to leave only words separated with one space """
        clean_text = re.sub(CLEANER_PATTERN, '', text.strip())
        return re.sub(r'( {2,}|[\s]+)', ' ', clean_text)

    @staticmethod
    def _get_md5(binary_data: bytes) -> str:
        return hashlib.md5(binary_data).hexdigest()

    @staticmethod
    def _aby_csv_rule(text: str) -> str:
        """ Rule to parse CSV files from Abyss game """
        # FIXME: Not good way to do methods only for abyss but use for all (костыль для игры)
        if text.startswith(r'u,') or text.startswith('a,'):
            return text[2:-2]  # FIXME  - text len can be 2
        elif text.startswith('[') and text.endswith(']'):
            return text[1:-1]
        return text.strip()

    # @staticmethod
    # def _filename_from_path(path, suffix=None):
    #     file_name = os.path.basename(path)
    #     if not suffix:
    #         return file_name
    #     name, ext = os.path.splitext(file_name)
    #     return f'{name}-{suffix}{ext}'

    # @staticmethod
    # def escape(string_val):   # TODO: Check needed
    #     """
    #     Escapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in
    #     the given string ``string_val`` and returns it.
    #     """
    #     return string_val.replace('\\', r'\\')\
    #              .replace('\t', r'\t')\
    #              .replace('\r', r'\r')\
    #              .replace('\n', r'\n')\
    #              .replace('\"', r'\"')
    #
    # @staticmethod
    # def unescape(string_val):   # TODO: Check needed
    #     """
    #     Unescapes the characters ``\\\\``, ``\\t``, ``\\n``, ``\\r`` and ``"`` in
    #     the given string ``string_val`` and returns it.
    #     """
    #     def unescape_repl(m):
    #         m = m.group(1)
    #         if m == 'n':
    #             return '\n'
    #         if m == 't':
    #             return '\t'
    #         if m == 'r':
    #             return '\r'
    #         if m == '\\':
    #             return '\\'
    #         return m  # handles escaped double quote
    #     return re.sub(r'\\(\\|n|t|r")', unescape_repl, string_val)
