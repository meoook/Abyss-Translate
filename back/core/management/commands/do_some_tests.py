from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Translated
from core.services.file_interface.file_interface import FileInterface


class Command(BaseCommand):
    help = 'Manager to create some test with current model'

    def handle(self, *args, **options):
        # file_api = FileInterface(3)
        # #
        # file_api.create_translated_copy(18)

        # User.objects.all().delete()

        for copy_info in Translated.objects.filter(need_refresh=True).values('file__id', 'language__id'):
            file_manager = FileInterface(copy_info['file__id'])
            file_manager.translated_copy_refresh(copy_info['language__id'])
