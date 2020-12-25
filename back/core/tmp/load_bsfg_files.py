import os
import shutil

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from core.models import Folder, File, Language
from core.services.file_interface.file_interface import FileInterface

""" THIS IS TEMPORARY FILE - ARCHIVE AFTER LOADED IN PRODUCTION """


class AbyMigrator:
    def __init__(self, folder_id: int):
        self.__folder_id = folder_id

    def start_parsing(self):
        if self.__prepare_data(self.__folder_id):
            _paths = (self.__path_source_orig, self.__path_dst)
            print('START PARSING {} FILES FROM {} TO {}'.format(self.__stats['begin_orig'], *_paths))
            print('WITH {} TRANSLATE FILES FROM {}'.format(self.__stats['begin_tr'], self.__path_source_tr))
            self.__iterate_source_folder()
            shutil.rmtree(self.__path_source_orig)
            shutil.rmtree(self.__path_source_tr)
            print('PARSED {} FILES FROM {} TO {}'.format(self.__stats['finished'], *_paths))
            print('PARSED {} TRANSLATES FROM {}'.format(self.__stats['with_tr'], self.__path_source_tr))
            [print(f'FILE {file_name} not found in translates') for file_name in self.__not_found_tr_list]
        else:
            print(f'UNKNOWN FOLDER {self.__folder_id}')

    def __prepare_data(self, folder_id) -> bool:
        try:
            _folder = Folder.objects.get(id=folder_id)
        except ObjectDoesNotExist:
            return False
        else:
            self.__prj_lang_orig_id = _folder.project.lang_orig.id                   # Const 75
            self.__english_id = self.__english_lang_id()                             # Const 18
            self.__path_source_orig = os.path.join(settings.MEDIA_ROOT, 'ru')        # Const ../users/ru
            self.__path_source_tr = os.path.join(settings.MEDIA_ROOT, 'en')          # Const ../users/en
            self.__path_source_tr_tmp = os.path.join(settings.MEDIA_ROOT, 'errors')  # Const ../users/errors
            self.__path_dst = self.__folder_path_from_instance(_folder)
            # self.__path_dst_tr = os.path.join(self.__path_dst, 'en')
            self.__file_list_ru = os.listdir(self.__path_source_orig)
            self.__file_list_en = os.listdir(self.__path_source_tr)
            self.__stats = {
                'begin_orig': len(self.__file_list_ru),
                'begin_tr': len(self.__file_list_en),
                'finished': 0,
                'with_tr': 0
            }
            self.__not_found_tr_list = []
            return True

    def __iterate_source_folder(self):
        for file_name in self.__file_list_ru:
            path_orig_old = os.path.join(self.__path_source_orig, file_name)
            if os.path.isfile(path_orig_old):
                # Move original file to users folder
                path_orig_new = self.__move_file(path_orig_old, self.__path_dst)
                self.__parse_file_and_copy(file_name, path_orig_new)

    def __parse_file_and_copy(self, file_name, file_path):
        # Create file object
        file_obj = File.objects.create(
            name=file_name,
            folder_id=self.__folder_id,
            lang_orig_id=self.__prj_lang_orig_id,
            data=file_path
        )
        file_manager = FileInterface(file_obj.id)
        file_manager.file_new(file_path, self.__prj_lang_orig_id)
        self.__stats['finished'] += 1
        if file_name in self.__file_list_en:
            path_tr_old = os.path.join(self.__path_source_tr, file_name)
            if os.path.isfile(path_tr_old):
                # Move original tr file to error folder (tmp)
                path_tr_new = self.__move_file(path_tr_old, self.__path_source_tr_tmp)
                file_manager.file_refresh(path_tr_new, self.__english_id, False)
                self.__stats['with_tr'] += 1
                return  # translate file found
        self.__not_found_tr_list.append(file_name)

    @staticmethod
    def __folder_path_from_instance(instance):
        """ Path of folder - users/<user_id>/<prj_id>/<folder_id> """
        _suffix = '{}/{}/{}'.format(instance.project.owner.id, instance.project.id, instance.id)
        return os.path.join(settings.MEDIA_ROOT, _suffix)

    @staticmethod
    def __english_lang_id():
        english = Language.objects.get(name__iexact='english')
        return english.id

    @staticmethod
    def __move_file(source_path, dst_dir):
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        return shutil.move(source_path, dst_dir)

