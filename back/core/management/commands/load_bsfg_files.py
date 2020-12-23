import os

from django.core.management.base import BaseCommand

from core.models import Folder, File
from core.services.file_interface.file_interface import FileInterface

""" THIS IS TEMPORARY FILE - ARCHIVE AFTER LOADED IN PRODUCTION """


class Command(BaseCommand):
    help = 'Manager to load BSFG html files with translated copy to localize system'

    def handle(self, *args, **options):
        root_path = r'C:\Projects\Abyss-Translate\back\users'
        folder_id = 21  # get from DB
        english_id = 18  # get from DB

        ru_dir = os.path.join(root_path, 'ru')
        en_dir = os.path.join(root_path, 'en')
        files_ru = os.listdir(ru_dir)
        files_en = os.listdir(en_dir)

        ok = 0
        trans = 0
        total = 0
        for file_name in files_ru:
            # if file_name != 'building_siegelist.htm':
                # print('skiping', file_name)
                # continue
            total += 1
            orig_path = os.path.join(ru_dir, file_name)
            trans_path = os.path.join(en_dir, file_name)
            if os.path.isfile(orig_path):
                ok += 1
                if file_name in files_en:
                    trans += 1
                else:
                    print(f'!! FILE:{file_name} have no copy {trans_path}')

                _folder = Folder.objects.select_related('project__lang_orig').get(id=folder_id)
                # Create file object
                prj_lang_orig_id: int = _folder.project.lang_orig.id
                file_obj = File.objects.create(name=file_name, folder=_folder, lang_orig_id=prj_lang_orig_id, data=orig_path)
                file_id = file_obj.id
                saved_file_path = file_obj.data.path
                file_manager = FileInterface(file_id)
                file_manager.file_new(saved_file_path, prj_lang_orig_id)
                # TODO: Do we need new manager for copy ?
                if file_name in files_en:
                    file_manager.file_refresh(trans_path, english_id, False)
        print(f'TOTAL:{total} OK:{ok} WITH COPY:{trans}')