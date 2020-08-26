import os
import re
import logging
from django.core.exceptions import ObjectDoesNotExist

from core.models import Translates, Translated
from core.services.utils import csv_validate_text

logger = logging.getLogger('django')


class CreateTranslatedCopy:
    """ Create translated copy of file for selected language """

    # TODO: SAVE ALL WORDS
    def __init__(self, id, language):
        self.__translate_file = None
        try:
            progress = Translated.objects.select_related('file', 'file__lang_orig', 'language').get(file__id=options['id'], language=options['language'])
            work_file = progress.file
            create_lang = progress.language
            if progress.items != work_file.items:
                self.stderr.write("File {} don't have full translate to {}".format(work_file.name, create_lang.name))
                return False
            translates = Translates.objects.select_related('mark').filter(mark__file=work_file)
        except Translated.DoesNotExist:
            self.stderr.write(f"File not found: {options['id']}")
            return False

    def any_def(self):
        self.stdout.write(f'Try create file from {work_file.name}(id:{work_file.id}) to language {create_lang.name}')
        dir_name = os.path.dirname(work_file.data.path)
        file_name, file_ext = os.path.splitext(work_file.data.path)
        self.__translate_file = open(os.path.join(dir_name, f'{file_name}-{create_lang.short_name}{file_ext}'), 'wb')
        if work_file.method == 'ue':
            self.__parse_as_ue(work_file, create_lang, translates)
        elif work_file.method == 'csv':
            self.__parse_as_csv(work_file, create_lang, translates)
        elif work_file.method == 'html':
            self.__parse_as_html(work_file, create_lang, translates)
        else:
            self.stderr.write(f"For file {work_file.id} wrong method : {work_file.method}")
            return False
        self.__translate_file.close()
        # FIXME: put file_obj with File Storage - or no need?
        progress.translate_copy = self.__translate_file.name
        progress.finished = True
        progress.save()
        self.stdout.write(f"File {self.__translate_file.name} successfully created")

    def __parse_as_ue(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            if file_obj.number_top_rows:
                for i, x in enumerate(filo):
                    if i == file_obj.number_top_rows - 1:
                        break
                    self.__translate_file.write(x)

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
                except Translates.DoesNotExist:
                    self.stderr.write(f"Can't find translate for number {object_number}")
                    return False

                if text == orig.text:   # Mb other check - trans.mark.text_binary.decode()
                    trans_object[5] = trans_object[5].replace(trans.mark.text_binary, trans.text.encode(file_obj.codec))
                [self.__translate_file.write(x) for x in trans_object]

    def __parse_as_csv(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            quotes_l = int(file_obj.options['quotes'][0]) if 'quotes' in file_obj.options else 0
            quotes_r = int(file_obj.options['quotes'][1]) if 'quotes' in file_obj.options else 0
            delimiter = file_obj.options['delimiter']
            delimiter_binary = delimiter.encode(file_obj.codec)
            fields = file_obj.options['fields']
            object_number = 0
            for i, row in enumerate(filo):
                if file_obj.number_top_rows and i < file_obj.number_top_rows:
                    self.__translate_file.write(row)
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
                    except Translates.DoesNotExist:
                        self.stderr.write(f"Can't find translate for number {object_number} column {idx}")
                        return False

                    if text != orig.text:
                        self.stderr.write(f"Can't merge file {file_obj.name} seems changes in BD.")
                        return False

                    text_binary = text_binary.replace(trans.mark.text_binary, trans.text.encode(file_obj.codec))
                    row_items.append(text_binary)
                self.__translate_file.write(delimiter_binary.join(row_items))

    def __parse_as_html(self, file_obj, create_lang, translates_objs):
        with open(file_obj.data.path, 'rb') as filo:
            data = filo.read().decode(file_obj.codec)
            texts_objs = []
            for idx, m in enumerate(re.finditer(r'\>\s*([^\<\>]+[^\s])\s*\<', data)):
                texts_objs.append({'number': idx, 'coordinates': m.span(1), 'text': m.group(1)})
            texts_objs.sort(key=lambda k: k['number'], reverse=True)

            for text_obj in texts_objs:
                try:
                    orig = translates_objs.get(mark__mark_number=text_obj['number'], language=file_obj.lang_orig)
                    trans = translates_objs.get(mark__mark_number=text_obj['number'], language=create_lang)
                except Translates.DoesNotExist:
                    self.stderr.write(f"Can't find translate for number {text_obj['number']}")
                    return False

                if text_obj['text'] != orig.text:
                    self.stderr.write(f"Can't merge file {file_obj.name} seems changes in BD.")
                    return False

                data = data[:text_obj['coordinates'][0]] + trans.text + data[text_obj['coordinates'][1]:]

            data_binary = data.encode(file_obj.codec)
            self.__translate_file.write(data_binary)
