import os
import re
import chardet
import hashlib
from datetime import datetime
from langdetect import detect, detect_langs
from html.parser import HTMLParser
import langdetect

# my_string.encode(errors='xmlcharrefreplace')
# 'кот cat'
#
# if __name__ == '__main__':
#     with open(r'C:\MIS\Projects\PY\AbbyTrans\users\ok2.txt', 'rb') as filo:
#         for row in filo:
#             for item in row.decode('utf8').split('\t'):
#                 try:
#                     int(item)
#                 except ValueError:
#                     re_clean = r'[\s\d\.\"\'\\\.\,\>\<\-\:\;\!\?\@\#\$\%\^\&\*\(\)\+\=\/\|\_\[\]\{\}]'
#                     item = re.sub(re_clean, '', item[2:-2])
#                     if len(item) > 0 and item[0] == 'i':
#                         print(detect(item[2:]), detect_langs(item), item)


def csv_validate_text(text):
    if re.match(r'^([N|n]one|[F|f]alse|[0-9]*\,+[0-9]*|[0-9\s]*|([^\s]*[\.\_][^\s]+)+)$', text):
        return False
    return text.replace('\r', '').replace('\n', '')


print('True' if csv_validate_text('50.0000') else 'False')
