import re
from django.core.management.base import BaseCommand

from core.models import Files, FileMarks, Translates, Translated
from core.utils.utils import get_md5, count_words, csv_validate_text


class Command(BaseCommand):
    help = 'Parse file by method and add parsed objects(to translate) to DB'
    __total_words = 0

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, default=None)

    def handle(self, *args, **options):
        if options['id'] is None:
            self.stderr.write('File ID not set')
            return False
        try:
            work_file = Files.objects.select_related('lang_orig').get(id=options['id'])
        except Files.DoesNotExist:
            self.stderr.write(f"File not found: {options['id']}")
            return False

        self.stdout.write('Load File {}(id:{}) language: {} method: {} options: {}'
                          .format(work_file.name, work_file.id, work_file.lang_orig, work_file.method, work_file.options))

        if work_file.method == 'ue':
            self.parse_as_ue(work_file)
        elif work_file.method == 'csv':
            self.parse_as_csv(work_file)
        elif work_file.method == 'html':
            self.parse_as_html(work_file)
        else:
            self.stderr.write(f"For file {work_file.id} wrong method : {work_file.method}")
            return False
        work_file.words = self.__total_words
        work_file.items = FileMarks.objects.filter(file=work_file).count()
        translate_to_ids = [x['id'] for x in list(work_file.folder.project.translate_to.values('id'))]
        work_file.translate_to.set(translate_to_ids)
        objs = [Translated(file=work_file, language_id=lang_id) for lang_id in translate_to_ids]
        Translated.objects.bulk_create(objs)
        work_file.state = 2   # parsed
        work_file.save()
        self.stdout.write(f"Success parsed file: {work_file.name}(id:{work_file.id})")

    def parse_as_ue(self, file_obj):
        with open(file_obj.data.path, 'rb') as filo:
            if file_obj.number_top_rows:
                for i, x in enumerate(filo):
                    if i == file_obj.number_top_rows - 1:
                        break
            object_number = 0
            while True:
                try:
                    object_number += 1
                    trans_object = [next(filo) for _ in range(7)]
                    text = trans_object[5].decode(file_obj.codec)[8:-3]     # FIXME [8:-3] -> re ^msgstr\ \"(.*)\"$
                    if len(text.strip()) == 0:
                        continue
                    text_md5, text_clear_md5 = get_md5(trans_object[5][8:-3], file_obj.codec)  # FIXME [8:-3]
                    words_count = count_words(text)
                    mark = FileMarks(
                        file=file_obj,
                        mark_number=object_number,
                        md5sum=text_md5,
                        md5sum_clear=text_clear_md5,
                        options=trans_object[3].decode(file_obj.codec)[9:-3],   # FIXME [9:-3]
                        words=words_count,
                        text_binary=trans_object[5][8:-3]
                    )
                    mark.save()
                    translate = Translates(
                        mark=mark,
                        language=file_obj.lang_orig,
                        text=text
                    )
                    translate.save()
                    self.__total_words += words_count
                except StopIteration:
                    break

    def parse_as_csv(self, file_obj):
        with open(file_obj.data.path, 'rb') as filo:
            quotes_l = int(file_obj.options['quotes'][0]) if 'quotes' in file_obj.options else 0
            quotes_r = int(file_obj.options['quotes'][1]) if 'quotes' in file_obj.options else 0
            delimiter = file_obj.options['delimiter']
            fields = file_obj.options['fields']
            object_number = 0
            for i, row in enumerate(filo):
                if file_obj.number_top_rows and i < file_obj.number_top_rows:
                    continue

                object_number += 1
                for idx, text in enumerate(row.decode(file_obj.codec).split(delimiter)):
                    if idx in fields:
                        text = csv_validate_text(text)
                        if text is False or len(text) <= quotes_l + quotes_r:
                            continue
                        text = text[quotes_l:-quotes_r] if quotes_r > 0 else text[quotes_l:]

                        text_binary = text.encode(file_obj.codec)
                        text_md5, text_clear_md5 = get_md5(text_binary, file_obj.codec)
                        words_count = count_words(text)

                        mark = FileMarks(
                            file=file_obj,
                            mark_number=object_number,
                            col_number=idx,
                            md5sum=text_md5,
                            md5sum_clear=text_clear_md5,
                            words=words_count,
                            text_binary=text_binary
                        )
                        mark.save()
                        translate = Translates(
                            mark=mark,
                            language=file_obj.lang_orig,
                            text=text
                        )
                        translate.save()
                        self.__total_words += words_count

    def parse_as_html(self, file_obj):
        with open(file_obj.data.path, 'rb') as filo:
            data = filo.read().decode(file_obj.codec)
            for idx, re_obj in enumerate(re.finditer(r'\>\s*([^\<\>]+[^\s])\s*\<', data)):
                text = re_obj.group(1)
                options = {'coordinates': re_obj.span(1)}
                if len(text.strip()) == 0:
                    continue
                words_count = count_words(text)   # TODO: Check words count
                text_binary = text.encode(file_obj.codec)
                text_md5, text_clear_md5 = get_md5(text_binary, file_obj.codec)
                mark = FileMarks(
                    file=file_obj,
                    mark_number=idx,
                    md5sum=text_md5,
                    md5sum_clear=text_clear_md5,
                    options=options,
                    words=words_count,
                    text_binary=text_binary,
                )
                mark.save()
                translate = Translates(
                    mark=mark,
                    language=file_obj.lang_orig,
                    text=text
                )
                translate.save()
                self.__total_words += words_count
