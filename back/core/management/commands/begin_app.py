import re
from django.core.management.base import BaseCommand

from core.models import Files, FileMarks, Translates, Translated


class Command(BaseCommand):
    help = 'Create test env'

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
        return False

