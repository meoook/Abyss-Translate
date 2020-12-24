from django.core.management.base import BaseCommand
from core.tmp.load_bsfg_files import AbyMigrator

""" THIS IS TEMPORARY FILE - ARCHIVE AFTER LOADED IN PRODUCTION """


class Command(BaseCommand):
    help = 'Manager to load BSFG html files with translated copy to localize system'

    def add_arguments(self, parser):
        parser.add_argument('folder_id', type=int, nargs='?', default=None)

    def handle(self, *args, **kwargs):
        if kwargs['folder_id'] is None:
            self.stdout.write(self.style.WARNING('error - set folder id where to parse files'))
            return
        else:
            self.stdout.write('PARSER: Start loading files...')
        migrator = AbyMigrator(kwargs['folder_id'])
        try:
            migrator.start_parsing()
        except Exception as err:
            self.stdout.write(self.style.ERROR(f'PARSER: Exception while parsing files: {err}'))
            return
        else:
            self.stdout.write(self.style.SUCCESS('PARSER: All files loaded'))
