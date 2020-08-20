import re
import chardet
from langdetect import detect, DetectorFactory
from html.parser import HTMLParser
from core.services.utils import get_md5, count_words, csv_validate_text

from datetime import datetime

# DetectorFactory.load_profile(
#     profile_directory='C:\Users\meok\.virtualenvs\AbbyTrans-lCvQG8K2\Lib\site-packages\langdetect\profiles')
# DetectorFactory.seed = 0    # Убирает "обучение" при распозновании языка

# TODO: Use clear text to find language (detect)

CSV_DELIMITERS = [',', '\t', ';', ' ']
UNREAL_ENGINE_STRINGS = [
    "Project-Id-Version",
    "POT-Creation-Date",
    "PO-Revision-Date",
    "Language-Team",
    "MIME-Version",
    "Content-Type",
    "Content-Transfer-Encoding",
    "Plural-Forms"
]


class DataGetInfo:
    def __init__(self, data, lang_orig, *args, **kwargs):
        self.__data = data
        self.__lang_orig = lang_orig
        self.__options = {}
        self.__error = None
        self.__method = None
        self.__lang = None

        self.__codec = chardet.detect(data[:1024 * 1024])['encoding']  # 1Mb ~ 8sec
        try:
            self.__data_decoded = self.__data.decode(self.__codec)
        except TypeError:
            self.__error = 'codec not found'
        except UnicodeDecodeError:
            self.__error = 'codec found with error'
        else:
            self.__get_info_init()

    @property
    def info(self):
        return {
            'codec': self.__codec,
            'method': self.__method,
            'options': self.__options,
            'language': self.__lang,    # detected language
            'error': self.__error
        }

    def __get_info_init(self):
        csv = self.__check_for_method_csv(self.__data_decoded[:4096])
        unreal = self.__check_for_method_ue(self.__data_decoded[:1024])
        html = self.__check_for_method_html(self.__data_decoded[:1024])
        if csv:
            self.__method = 'csv'
            self.__options['delimiter'] = csv
            if self.__lang_orig:
                self.__csv_get_options(csv)
            else:
                self.__error = 'method csv need original language'
        elif unreal > 50 and unreal > html:
            self.__method = 'ue'
            self.__ue_get_options()
        elif html > 50:
            self.__method = 'html'
            self.__http_get_structure()
        else:
            self.__error = 'method not found'

    @staticmethod
    def __check_for_method_ue(data_decoded):
        founded = 0
        for row in data_decoded.split('\n'):
            if row[0:7] == 'msgctxt' or row[0:6] == 'msgstr' or row[0:5] == 'msgid':
                founded += 1
                continue
            for ue_row in UNREAL_ENGINE_STRINGS:
                if ue_row in row:
                    founded += 1
                    break
        return 100 if founded > 10 else founded * 10

    @staticmethod
    def __check_for_method_html(data_decoded):
        parser = HTMLChecker()
        parser.feed(data=data_decoded)
        parser.close()
        return 100 if parser.founded > 20 else parser.founded * 5

    @staticmethod
    def __check_for_method_csv(data_decoded):
        for delimiter in CSV_DELIMITERS:
            array_of_rows_lens = []
            for row in data_decoded.split('\n'):
                split_row = row.split(delimiter)
                if isinstance(split_row, list) and len(split_row) > 1:
                    array_of_rows_lens.append(len(split_row))
                else:
                    break
            if len(array_of_rows_lens[:-1]) > 1 and len(set(array_of_rows_lens[:-1])) == 1:
                return delimiter
        return False

    def __csv_get_options(self, delimiter):
        """ Find language, quotes, column numbers(by lang)"""
        quotes = {'l1': [], 'l2': [], 'l3': [], 'l4': [], 'r1': [], 'r2': [], 'r3': [], 'r4': []}
        columns = {}
        top_rows = True
        # This values affect timing
        __row_check = 75          # number of rows to check by default
        __row_check_max = 100     # maximum allow rows to check
        for row_n, row in enumerate(self.__data_decoded.split('\n')):
            if row_n > __row_check:
                if self.__lang:
                    break
                elif __row_check < __row_check_max:
                    __row_check += 25
                else:
                    self.__error = 'original language not found'
                    return False
            for col_n, val in enumerate(row.split(delimiter)):
                text = csv_validate_text(val)
                if row_n == 0 and top_rows:
                    try:
                        float(val)
                        top_rows = False
                    except ValueError:
                        pass
                elif text and self.__lang_orig == detect(text):
                    columns[col_n] = columns[col_n] + 1 if col_n in columns else 1
                    if self.__lang is None:
                        self.__lang = self.__lang_orig
                    quotes['l1'].append(text[0])
                    quotes['l2'].append(text[1])
                    quotes['l3'].append(text[2])
                    quotes['l4'].append(text[3])
                    # val_back = val[:-1] if val[-1] == '\r' else val   # Каретка fix
                    quotes['r1'].append(text[-1])
                    quotes['r2'].append(text[-2])
                    quotes['r3'].append(text[-3])
                    quotes['r4'].append(text[-4])
        # Check for __error
        if self.__lang is None:
            self.__error = 'original language not found'
            return False
        # Find quotes
        left = 0
        right = 0
        if len(quotes['l1']) > 1 and len(set(quotes['l1'])) == 1:
            left = 1
            if len(set(quotes['l2'])) == 1:
                left = 2
                if len(set(quotes['l3'])) == 1:
                    left = 3
                    if len(set(quotes['l4'])) == 1:
                        left = 4
        if len(quotes['r1']) > 1 and len(set(quotes['r1'])) == 1:
            right = 1
            if len(set(quotes['r2'])) == 1:
                right = 2
                if len(set(quotes['r3'])) == 1:
                    right = 3
                    if len(set(quotes['r4'])) == 1:
                        right = 4
        # Method results
        self.__options['fields'] = [k for k, v in columns.items() if v > 1]
        self.__options['quotes'] = f'{left}{right}'
        if top_rows:
            self.__options['top_rows'] = 1

    def __ue_get_options(self):
        start = None
        for row_n, row in enumerate(self.__data_decoded.split('\n')):
            if row_n > 30:
                self.__error = 'first row height to big for UE file'
                break
            if row in ('', '\r'):       # Usefull data palced after first empty row
                if start:
                    height = row_n - start
                    if height != 7:     # Default number of rows for 1 obj in UE file
                        self.__error = f'cell height is not standard - {height}'
                    break
                else:
                    start = row_n
                    self.__options['top_rows'] = row_n
        lang_checker = []
        for row_n, row in enumerate(self.__data_decoded.split('\n')):
            if row_n > 100:
                break
            if row[:7] == 'msgstr ' and len(row[8:-2]) > 2:
                if self.__lang_orig and self.__lang_orig != detect(row[8:-2]):
                    lang_checker.append(1)  # Number of errors
                else:
                    lang_checker.append(row[8:-2])  # Add words to check
        if self.__lang_orig:
            if len(lang_checker) > 8:    # Number of allowed errors (errors are possible)
                self.__error = 'language not detected'
            else:
                self.__lang = self.__lang_orig
        else:
            self.__lang = detect(''.join(lang_checker))
            if self.__lang is None:
                self.__error = 'language not detected'

    def __http_get_structure(self):
        texts = re.findall(r'\>\s*([^\<\>]+[^\s])\s*\<', self.__data_decoded[:2048])
        self.__options['count'] = len(texts)
        all_texts_langs = [detect(x) for x in texts]
        if len(set(all_texts_langs)) == 1:
            self.__lang = all_texts_langs[0]
        else:
            lang = detect(''.join(texts))
            if lang:
                self.__lang = lang
                if self.__lang_orig and self.__lang_orig != lang:
                    self.__error = f'incorrect original language {lang}'
            else:
                self.__error = 'no language found'


class HTMLChecker(HTMLParser):
    founded = 0
    # HTML INSIDE TEXT RE = \>\s*([^\<\>]+[^\s])\s*\<

    def handle_starttag(self, tag, attrs):
        self.founded += 1

    def handle_endtag(self, tag):
        self.founded += 1

    # def handle_data(self, data):
    #     pass

    def error(self, message):
        # print('ERROR while HTML check', message)
        pass
