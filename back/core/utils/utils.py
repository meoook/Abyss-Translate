import hashlib
import re

def get_md5_f(binary_data, clear=False):
    """ If clear - also return md5 of cleaned text to search same text """
    md5sum = hashlib.md5(binary_data).hexdigest()
    if clear:
        re_clean = r'[\s\d\.\"\'\\\.\,\>\<\-\:\;\!\?\@\#\$\%\^\&\*\(\)\+\=\/\|\_\[\]\{\}]'
        clean = re.sub(re_clean.encode(), b'', binary_data)
        md5sum_only_letters = hashlib.md5(clean).hexdigest()
        return md5sum, md5sum_only_letters
    return md5sum

def get_md5(binary_data, codec=None):
    """ If codec set - also return md5 of cleaned text to search same text """
    md5sum = hashlib.md5(binary_data).hexdigest()
    if codec:
        re_clean = r'[\s\d\.\"\'\\\.\,\>\<\-\:\;\!\?\@\#\$\%\^\&\*\(\)\+\=\/\|\_\[\]\{\}]'
        clean = re.sub(re_clean, '', binary_data.decode(codec))
        md5sum_only_letters = hashlib.md5(clean.encode(codec)).hexdigest()
        return md5sum, md5sum_only_letters
    return md5sum


def count_words(text):
    """ App function to find number of words(payment) in text """
    word_min_len_to_count = 2
    re_clean = r'[\d\.\"\'\\\.\,\>\<\-\:\;\!\?\@\#\$\%\^\&\*\(\)\+\=\/\|\_\[\]\{\}]'
    clean = re.sub(re_clean, '', text)
    return len([x for x in clean.split(' ') if len(x) > word_min_len_to_count])


def csv_validate_text(text):
    # if re.match('^([N|n]one|[F|f]alse|[0-9]*\,+[0-9]*|[0-9\s]*|([^\s]*[\.\_][^\s]+)+)$', text):
    text = text.strip()
    if re.match('^([N|n]one|[F|f]alse|[T|t]rue|[0-9]*\,+[0-9]*|[0-9\s]*|[^\s]*[\.\_][^\s]+)$', text):
        return False
    return text
