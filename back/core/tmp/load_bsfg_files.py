import os

from core.models import Folder, File
from core.services.file_interface.file_interface import FileInterface


def load_data_test():
    root_path = r'C:\+migration\from_repo'
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
        total += 1
        orig_path = os.path.join(ru_dir, file_name)
        trans_path = os.path.join(en_dir, file_name) if file_name in files_en else ''
        if os.path.isfile(orig_path):
            ok += 1
            if trans_path:
                trans += 1
            else:
                print(f'FILE:{file_name} have no copy')

            _folder = Folder.objects.select_related('project__lang_orig').get(id=folder_id)
            # Create file object
            prj_lang_orig_id: int = _folder.project.lang_orig.id
            file_obj = File.objects.create(name=file_name, folder=folder_id, lang_orig=prj_lang_orig_id, data=orig_path)
            file_id = file_obj.id
            saved_file_path = file_obj.data.path
            file_manager = FileInterface(file_id)
            file_manager.file_new(saved_file_path, prj_lang_orig_id)
            # TODO: Do we need new manager for copy ?
            if trans_path:
                file_manager.file_refresh(trans_path, english_id, False)


if __name__ == '__main__':
    load_data_test()
