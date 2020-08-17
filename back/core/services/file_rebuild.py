import re

from django.db.models import Sum, Count

from core.models import Files, FileMarks, Translates, Translated
from core.utils.utils import get_md5, count_words, csv_validate_text


class FileRebuild:
    """ Rebuild translates after file update """
    def __init__(self, f_path, codec, f_name, file_id, f_lang_id, f_method, f_options):
        self.__marks_to_check = {}
        self.__marks_to_update = []
        self.__marks_to_add = []
        self.stats = {}
        self.error = None
        # Check params
        if not isinstance(file_id, int) or not isinstance(lang_orig_id, int) or not f_method or not f_path:
            self.error = 'Wrong arguments'
        else:
        	self.__init_build(file_id, f_method, f_path, codec, f_lang_id, f_options)

    def __itit_build(self, file_id, method, file_path, codec, lang_orig_id, options):
        # Get file marks if file was before
        for x in FileMarks.objects.filter(file_id=file_id):
            self.__marks_to_check[x.id] = {
                'mark_number': x.mark_number,
                'col_number': x.col_number,
                'md5sum': x.md5sum,
                'options': x.options
            }
        # New or rebuild
        rebuild = len(self.__marks_to_check) == 0
        # Get self.__marks_to_*** arrays
        with open(file_path, 'rb') as filo:
			if method == 'ue':
				self.parse_as_ue(filo, codec, options)
			elif method == 'csv':
				self.parse_as_csv(filo, codec, options)
			elif method == 'html':
				self.parse_as_html(filo, codec, options)
			else:
				self.error = f"Wrong method {method} for file {file_name}{file_id}")
				return False
        self.__build_marks(file_id, lang_orig_id, rebuild)
        # Get file stats
        stats = FileMarks.objects.filter(file_id=file_id).aggregate(items_count=Count('id'), total_words=Sum('words'))
        self.stats['words'] = stats['total_words']
        self.stats['items'] = stats['items_count']
		return True

    def parse_as_ue(self, filo, codec, f_options):
		# Pass header
		if 'top_rows' in f_options and f_options['top_rows']:
			for i, _ in enumerate(filo):
				if i == f_options['top_rows'] - 1:
					break
		# Parsing file
		object_number = 0
		while True:
			try:
				object_number += 1
				trans_object = [next(filo) for _ in range(7)]
			except StopIteration:
				break
			text = trans_object[5].decode(codec)[8:-3]     # FIXME [8:-3] -> re ^msgstr\ \"(.*)\"$
			if len(text.strip()) == 0:
				continue
			options = trans_object[3].decode(codec)[9:-3]
			self.__check_or_create_mark(object_number, None, text, codec, options)

    def parse_as_csv(self, filo, codec, options):
		quotes_l = int(options['quotes'][0]) if 'quotes' in options else 0
		quotes_r = int(options['quotes'][1]) if 'quotes' in options else 0
		delimiter = options['delimiter']
		fields = options['fields']
		object_number = 0
		for i, row in enumerate(filo):
			if 'top_rows' in options and options['top_rows'] > i:
				continue
			object_number += 1
			for idx, text in enumerate(row.decode(codec).split(delimiter)):
				if idx in fields:
					text = csv_validate_text(text)
					if text is False or len(text) <= quotes_l + quotes_r:
						continue
					text = text[quotes_l:-quotes_r] if quotes_r > 0 else text[quotes_l:]
					self.__check_or_create_mark(object_number, idx, text, codec)

    def parse_as_html(self, filo, codec, options):
		data = filo.read().decode(codec)
		for idx, re_obj in enumerate(re.finditer(r'\>\s*([^\<\>]+[^\s])\s*\<', data)):
			text = re_obj.group(1)
			options = {'coordinates': re_obj.span(1)}
			if len(text.strip()) == 0:
				continue
			self.__check_or_create_mark(idx, None, text, codec, options)

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

    def __build_marks(self, file_id, lang_orig_id, rebuild):
        """ Create/update/delete marks after file parse """
        # Delete/Update mark
        if rebuild:
            FileMarks.objects.filter(id__in=self.__marks_to_check.keys()).delete()
            for mark_item in sorted(self.__marks_to_update, key=lambda m: m['new_number'], reverse=True):   # TODO: sort by col
                FileMarks.objects.filter(id=mark_item['id'])\
                    .update(mark_number=mark_item['new_number'], col_number=mark_item['col_number'])
        # Create new mark and original translate
        for mark_item in self.__marks_to_add:
            mark = FileMarks(
                file_id=file_id,
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
                language_id=lang_orig_id,
                text=mark_item['text']
            )
            translate.save()
