import re
import logging

from django.db.models import Sum, Count

from core.models import Files, FileMarks, Translates, Translated
from core.utils.utils import get_md5, count_words, csv_validate_text

logger = logging.getLogger('logfile')


class FileRebuild:
    """ Rebuild translates after file update """
    def __init__(self, file_id):
        self.__marks_to_check = {}
        self.__marks_to_update = []
        self.__marks_to_add = []

        # Check params
        if file_id is None:
            logger.error('File ID not set')
        else:
            try:
                work_file = Files.objects.select_related('lang_orig').get(id=file_id)
                file_options = [work_file.name, work_file.id, work_file.lang_orig, work_file.method, work_file.options]
            except Files.DoesNotExist:
                logger.warning(f"File not found: {file_id}")
        # Get file marks if file was before
        for x in FileMarks.objects.filter(file=work_file):
            self.__marks_to_check[x.id] = {
                'mark_number': x.mark_number,
                'col_number': x.col_number,
                'md5sum': x.md5sum,
                'options': x.options
            }
        # New or rebuild
        if len(self.__marks_to_check) == 0:
            logger.info('Build file marks {}(id:{}) language: {} method: {} options: {}'.format(*file_options))
            rebuild = False
        else:
            rebuild = True
            logger.info('Rebuild file marks {}(id:{}) language: {} method: {} options: {}'.format(*file_options))
        # Get self.__marks_to_*** arrays
        if work_file.method == 'ue':
            self.parse_as_ue(work_file)
        elif work_file.method == 'csv':
            self.parse_as_csv(work_file)
        elif work_file.method == 'html':
            self.parse_as_html(work_file)
        else:
            self.stderr.write(f"For file {work_file.id} wrong method : {work_file.method}")
            return False
        self.__build_marks(work_file, rebuild)
        # Update file stats
        # self.__items_count = FileMarks.objects.filter(file=file_obj, translates__language=file_obj.lang_orig).count()
        stats = FileMarks.objects.filter(file=work_file).aggregate(items_count=Count('id'), total_words=Sum('words'))
        work_file.words = stats['total_words']
        work_file.items_count = stats['items_count']
        if rebuild is False:
            translate_to_ids = work_file.folder.project.translate_to.values_list('id', flat=True)
            work_file.translate_to.set(translate_to_ids)
            objs = [Translated(file=work_file, language_id=lang_id) for lang_id in translate_to_ids]
            Translated.objects.bulk_create(objs)
            work_file.state = 2   # parsed
        work_file.save()
        self.stdout.write(f"Success created file marks: {work_file.name}(id:{work_file.id})")

    def parse_as_ue(self, file_obj):
        with open(file_obj.data.path, 'rb') as filo:
            if file_obj.number_top_rows:
                for i, _ in enumerate(filo):
                    if i == file_obj.number_top_rows - 1:
                        break
            object_number = 0
            while True:
                try:
                    object_number += 1
                    trans_object = [next(filo) for _ in range(7)]
                except StopIteration:
                    break
                text = trans_object[5].decode(file_obj.codec)[8:-3]     # FIXME [8:-3] -> re ^msgstr\ \"(.*)\"$
                if len(text.strip()) == 0:
                    continue
                options = trans_object[3].decode(file_obj.codec)[9:-3]
                self.__check_or_create_mark(object_number, None, text, file_obj.codec, options)

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
                        self.__check_or_create_mark(object_number, idx, text, file_obj.codec)

    def parse_as_html(self, file_obj):
        with open(file_obj.data.path, 'rb') as filo:
            data = filo.read().decode(file_obj.codec)
            for idx, re_obj in enumerate(re.finditer(r'\>\s*([^\<\>]+[^\s])\s*\<', data)):
                text = re_obj.group(1)
                options = {'coordinates': re_obj.span(1)}
                if len(text.strip()) == 0:
                    continue
                self.__check_or_create_mark(idx, None, text, file_obj.codec, options)

    def __check_or_create_mark(self, mark_n, col_n, text, codec, options=None):
        """ Find what array mark to add (leave to remove, update, create) """
        text_binary = text.encode(codec)
        text_md5, text_clear_md5 = get_md5(text_binary, codec)
        # Try to find same in created marks
        for mark_id, mark_item in self.__marks_to_check.items():
            if mark_item['md5sum'] == text_md5:
                # Pop founded from items to del
                founded = self.__marks_to_check.pop(mark_id)
                # Check if need to update
                if founded['mark_number'] != mark_n:
                    self.__marks_to_update.append({'id': mark_id, 'new_number': mark_n, 'col_number': col_n})
                break
        else:
            # Prepare item to create
            words_count = count_words(text)
            self.__marks_to_add.append({
                'mark_number': mark_n,
                'col_number': col_n,
                'md5sum': text_md5,
                'md5sum_clear': text_clear_md5,
                'options': options,
                'words': words_count,
                'text_binary': text_binary,
                'text': text
            })

    def __build_marks(self, file_obj, rebuild):  # new_items, to_del_ids=None, update_arr=None):
        """ Create/update/delete marks after file parse """
        # Delete/Update mark
        if rebuild:
            FileMarks.objects.filter(id__in=self.__marks_to_check.keys()).delete()
            for mark_item in sorted(self.__marks_to_update, key=lambda m: m['new_number'], reverse=True):   # TODO: sort by col
                FileMarks.objects.filter(id=mark_item['id'])\
                    .update(mark_number=mark_item['new_number'], col_number=mark_item['col_number'])
        # Create new mark and original translate
        for mark_item in self.__marks_to_add:
            print('MARK ITEM', mark_item)
            mark = FileMarks(
                file_id=file_obj.id,
                mark_number=mark_item['mark_number'],
                col_number=mark_item['col_number'],
                md5sum=mark_item['md5sum'],
                md5sum_clear=mark_item['md5sum_clear'],
                options=mark_item['options'],
                words=mark_item['words'],
                text_binary=mark_item['text_binary']
            )
            mark.save()
            translate = Translates(
                mark=mark,
                language=file_obj.lang_orig,
                text=mark_item['text']
            )
            translate.save()
