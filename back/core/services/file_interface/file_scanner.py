import re

import chardet
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from core.services.file_interface.id_finder import UniqueIDLookUp
from core.services.file_interface.parser_utils import ParserUtils
from core.services.file_interface.quote_finder import TextQuoteFinder


class FileScanner(ParserUtils):
    """ Get method of file and other info (file_manager subclass) """
    __CSV_DELIMITERS = ['\t', ',', ';', ' ']

    def __init__(self, path: str, lang_orig_short_name: str = None):
        self.__lang: str = lang_orig_short_name
        self.__options: dict = {}  # quotes, work columns and FID lookup for csv
        self.__method: str = ''
        self.__codec: str = ''
        self.__error: str = ''
        self.__warning: str = ''
        if self.__set_basic_info(path):
            self.__find_method()

    def __repr__(self) -> dict:
        return {
            'codec': self.__codec,
            'method': self.__method,
            'options': self.__options,
            'warning': self.__warning,
            'error': self.__error,
        }

    def __getattr__(self, attr: str):
        return self.__repr__()[attr]

    @property
    def info(self) -> dict:
        """ Need param to iterate fields """
        return self.__repr__()

    @property
    def data(self) -> str:
        """ Return decoded data - can be used in other classes - for memory optimisation """
        return self.__data

    def __set_basic_info(self, path: str) -> bool:
        """ Read file, find codec and check it """
        try:
            with open(path, 'rb') as filo:
                data = filo.read()
        except FileNotFoundError:
            self.__error = 'file not found'
        except IOError:
            self.__error = 'file read error'
        else:
            codec = chardet.detect(data[:1024 * 2048])['encoding']  # 1Mb ~ 8sec
            try:
                decoded_data = data.decode(codec)
                self.__data = decoded_data
                self.__codec = codec
                return True
            except TypeError:
                self.__error = 'unknown codec'
            except UnicodeDecodeError:
                self.__error = 'codec found with error'
        return False

    def __find_method(self) -> None:
        if self.__method_check_csv():
            return self.__deep_scan_csv()
        elif self.__method_check_ue():
            return self.__deep_scan_ue()
        elif self.__method_check_html():
            return
        # Default method 'row'
        self.__method_default()

    def __method_default(self) -> None:
        """ Default method is 'row' (one row = one value) """
        self.__method = 'row'
        clean_text = self._clean_text(self.__data)
        self.__find_lang_in_text(clean_text)

    def __method_check_ue(self) -> bool:
        """ File check by gettext (used in Unreal Engine) """
        founded = 0
        for idx, row in enumerate(self.__data.splitlines()):
            # FIXME: It's really possible that can be html file where 'msgid' or 'msgstr' will be at start of line :)
            if re.search('^msg(id|str)', row):
                founded += 1
                continue
            if founded > 2:
                self.__method = 'ue'
                return True
            if idx > 30:
                break
        return False

    def __method_check_csv(self) -> bool:
        for delimiter in self.__CSV_DELIMITERS:
            array_of_rows_lens = []
            for idx, row in enumerate(self.__data.splitlines()):
                split_row = row.split(delimiter)
                if isinstance(split_row, list) and len(split_row) > 1:
                    array_of_rows_lens.append(len(split_row))
                else:
                    break
                if idx > 2:  # Parse 4 rows
                    break
            if len(array_of_rows_lens) == 4 and len(set(array_of_rows_lens)) == 1:
                self.__options['delimiter'] = delimiter
                self.__method = 'csv'
                return True
        return False

    def __method_check_html(self) -> bool:
        all_tags = re.findall(r'<[^><]+>', self.__data)
        if len(all_tags) > 1:  # Is HTML STRUCTURE
            self.__method = 'html'
            texts = re.findall(r'>\s*([^<>]+[^\s])\s*<', self.__data)
            # if len(texts) < 1:    # TODO: Add values count check - for not valid values in HTML (if 0 - pass file)
            #     return False  # HTML with no text
            self.__find_lang_in_text(''.join(texts))
            return True
        return False

    def __deep_scan_csv(self) -> None:
        """ Find header row, quotes, language, columns, fid lookup method """  # FIXME: scan time is too long
        quotes_finder = TextQuoteFinder()
        columns = {}   # To find what columns have *valid* text
        columns_lookup_id = UniqueIDLookUp()  # To find column(s) unique for all file
        all_clean_texts = ''
        top_rows = True  # File with header row by default

        for row_n, row in enumerate(self.__data.splitlines()):
            for col_n, val in enumerate(row.split(self.__options['delimiter']), start=1):
                if not val:  # Fix end row
                    continue
                if row_n == 0 and top_rows:  # Check first row if it's header!
                    try:
                        float(val)  # If top row have int/float - it's not a header row (file without header row)
                        top_rows = False
                    except ValueError:
                        pass  # File with header row - is ok
                    finally:
                        continue
                # Validate and serialize text
                _fixed_text = self._aby_csv_rule(val)
                text = self.__csv_text_serializer(_fixed_text)
                if text:
                    # Put support variables for language, fID and columns finders methods
                    quotes_finder.value = text
                    all_clean_texts += self._clean_text(text)
                    columns[col_n] = columns[col_n] + 1 if col_n in columns else 1
                else:
                    try:
                        int_val = int(val)  # Try to get fID from numeric fields
                    except ValueError:
                        continue
                    else:
                        columns_lookup_id[col_n] = abs(int_val)
            # If top row is header - put it in lookup method
            if row_n == 0 and top_rows:
                columns_lookup_id.header = row.split(self.__options['delimiter'])
            else:  # Next row trigger for lookup method
                columns_lookup_id.next_row()
        """ Results """
        self.__options['quotes'] = quotes_finder.value
        self.__options['top_rows'] = 1 if top_rows else 0
        self.__options['fields'] = [k for k, v in columns.items() if v > 1]
        self.__options['fid_lookup'] = columns_lookup_id.formula
        # Warning and errors
        if not self.__options['fields']:
            self.__error = 'no fields to translate'
        else:
            self.__find_lang_in_text(all_clean_texts)  # Check language
        if self.__options['fields'] and not self.__options['fid_lookup']:  # Don't cover "no fields error"
            self.__warning = 'fid lookup method not found'

    def __deep_scan_ue(self) -> None:
        """ Find FID lookup method, language, head rows """
        validate_unique_id = UniqueIDLookUp()
        all_clean_texts = ''
        top_rows = 0

        for row_n, row in enumerate(self.__data.splitlines(), start=1):
            if not top_rows and not row.strip():  # If the row is empty
                top_rows = row_n - 1  # Gettext item start with empty field
                continue

            if not row:
                validate_unique_id.next_row()
            text = self.__ue_text_serializer(row)
            if text:
                if row.startswith('msgid'):
                    validate_unique_id[1] = text
                elif row.startswith('msgctxt'):
                    validate_unique_id[2] = text
                else:  # msgstr
                    all_clean_texts += self._clean_text(text)
        """ Results """
        self.__options['top_rows'] = top_rows
        # Warning and errors
        self.__find_lang_in_text(all_clean_texts)  # Check language
        self.__options['fid_lookup'] = validate_unique_id.formula
        if not self.__options['fid_lookup']:
            self.__warning = 'fid lookup method not found'

    def __find_lang_in_text(self, text: str) -> None:
        """ Detected language and check it with language set by user """
        if not self.__lang:
            self.__warning = 'original language not set'
            return
        try:  # FIXME: change lang lib or load profiles before
            language = detect(text)
        except LangDetectException:
            self.__warning = 'can\'t detect language'
            return
        if not language:  # TODO: language library error - mb not for user
            self.__warning = 'language not found'
        elif self.__lang != language:
            self.__warning = f'incorrect original language {language}'

    @staticmethod
    def __csv_text_serializer(text: str) -> str:
        """ Check cell if it's have a valid text inside. Invalid are: aaa.bbb, aaa_bbb, bool and int types """
        if not re.match(r'^(none|false|true|[\W\-+_0-9]+|[^\s]*[._]+[^\s]*[^.])$', text, re.IGNORECASE):
            return text

    @staticmethod
    def __ue_text_serializer(text: str) -> str:
        """ Unreal Engine use 'gettext'(.po) files for translates - check format """
        search = re.search(r'^msg(?:id|str|ctxt) "(.+)"\s?$', text, re.IGNORECASE)
        if search:
            return search.group(1)
