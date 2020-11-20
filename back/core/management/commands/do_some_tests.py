from django.core.management.base import BaseCommand

from core.services.file_interface.file_interface import FileModelAPI


class Command(BaseCommand):
    help = 'Manager to create some test with current model'

    def handle(self, *args, **options):
        file_api = FileModelAPI(4)

        file_api.create_translated_copy(22)

