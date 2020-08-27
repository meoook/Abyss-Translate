import os
import re
import logging
from django.core.exceptions import ObjectDoesNotExist

from core.models import Translates, Languages
from core.services.utils import csv_validate_text

logger = logging.getLogger('django')


class CreateTranslatedCopy:
    """ Create translated copy of file for selected language """

    # TODO: REMAKE AS BUILD
    def __init__(self, file_obj, language_to):
        self.copy_name = None
        try:
            lang_cr = Languages.objects.get(id=language_to)
            translates = Translates.objects.select_related('mark').filter(mark__file=file_obj)
        except ObjectDoesNotExist:
            logger.error(f'Language not found {language_to}')
        else:
            self.__create_copy(file_obj, lang_cr, translates)

    def __create_copy(self, work_file, create_lang, translates):
        dir_name = os.path.dirname(work_file.data.path)
        file_name, file_ext = os.path.splitext(work_file.data.path)
        trans_copy_name = f'{file_name}-{create_lang.short_name}{file_ext}'
        logger.info(f'Creating translated copy {trans_copy_name} for file id: {work_file.id})')
        self.__translated_copy = open(os.path.join(dir_name, trans_copy_name), 'wb')
        if work_file.method == 'ue':
            self.__parse_as_ue(work_file, create_lang, translates)
        elif work_file.method == 'csv':
            self.__parse_as_csv(work_file, create_lang, translates)
        elif work_file.method == 'html':
            self.__parse_as_html(work_file, create_lang, translates)
        else:
            logger.critical(f"For file {work_file.id} wrong method : {work_file.method}")
        self.__translated_copy.close()
        self.copy_name = self.__translated_copy.name
        logger.info(f'Translated copy {self.copy_name} created for file id: {work_file.id})')

    def __parse_as_ue(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            if file_obj.number_top_rows:
                for i, x in enumerate(filo):
                    if i == file_obj.options['top_rows'] - 1:
                        break
                    self.__translated_copy.write(x)
            object_number = 0
            while True:
                try:
                    object_number += 1
                    trans_object = [next(filo) for _ in range(7)]
                    text = trans_object[5].decode(file_obj.codec)[8:-3]     # FIXME [8:-3]
                    if len(text.strip()) == 0:
                        continue
                except StopIteration:
                    break
                try:
                    orig = translates_objs.get(mark__mark_number=object_number, language=file_obj.lang_orig)
                    trans = translates_objs.get(mark__mark_number=object_number, language=create_lang)
                except ObjectDoesNotExist:
                    logger.error(f"Can't find translate for number {object_number}")
                    return False

                if text == orig.text:   # Mb other check - trans.mark.text_binary.decode()
                    trans_object[5] = trans_object[5].replace(trans.mark.text_binary, trans.text.encode(file_obj.codec))
                [self.__translated_copy.write(x) for x in trans_object]

    def __parse_as_csv(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            quotes_l = int(file_obj.options['quotes'][0]) if 'quotes' in file_obj.options else 0
            quotes_r = int(file_obj.options['quotes'][1]) if 'quotes' in file_obj.options else 0
            delimiter = file_obj.options['delimiter']
            delimiter_binary = delimiter.encode(file_obj.codec)
            fields = file_obj.options['fields']
            object_number = 0
            for i, row in enumerate(filo):
                if file_obj.number_top_rows and i < file_obj.options['top_rows']:
                    self.__translated_copy.write(row)
                    continue
                object_number += 1
                row_items = []
                for idx, text in enumerate(row.decode(file_obj.codec).split(delimiter)):
                    text_binary = text.encode(file_obj.codec)
                    if idx not in fields:
                        row_items.append(text_binary)
                        continue
                    text = csv_validate_text(text)
                    if text is False or len(text) <= quotes_l + quotes_r:
                        row_items.append(text_binary)
                        continue
                    text = text[quotes_l:-quotes_r] if quotes_r > 0 else text[quotes_l:]

                    try:
                        orig = translates_objs.get(mark__mark_number=object_number, mark__col_number=idx, language=file_obj.lang_orig)
                        trans = translates_objs.get(mark__mark_number=object_number, mark__col_number=idx, language=create_lang)
                    except ObjectDoesNotExist:
                        logger.error(f"Can't find translate for number {object_number} column {idx}")
                        return False

                    if text != orig.text:
                        logger.error(f"Can't merge file {file_obj.name} seems changes in BD.")
                        return False

                    text_binary = text_binary.replace(trans.mark.text_binary, trans.text.encode(file_obj.codec))
                    row_items.append(text_binary)
                self.__translated_copy.write(delimiter_binary.join(row_items))

    def __parse_as_html(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            data = filo.read().decode(file_obj.codec)
            texts_objs = []
            for idx, m in enumerate(re.finditer(r'>\s*([^<>]+[^\s])\s*<', data)):
                texts_objs.append({'number': idx, 'coordinates': m.span(1), 'text': m.group(1)})
            texts_objs.sort(key=lambda k: k['number'], reverse=True)

            for text_obj in texts_objs:
                try:
                    orig = translates_objs.get(mark__mark_number=text_obj['number'], language=file_obj.lang_orig)
                    trans = translates_objs.get(mark__mark_number=text_obj['number'], language=create_lang)
                except ObjectDoesNotExist:
                    logger.error(f"Can't find translate for number {text_obj['number']}")
                    return False

                if text_obj['text'] != orig.text:
                    logger.error(f"Can't merge file {file_obj.name} seems changes in BD.")
                    return False

                data = data[:text_obj['coordinates'][0]] + trans.text + data[text_obj['coordinates'][1]:]

            data_binary = data.encode(file_obj.codec)
            self.__translated_copy.write(data_binary)
