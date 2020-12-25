import os
import shutil

from django.contrib.auth.models import User, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from core.models import Project, Folder, Language, File
from core.services.file_interface.file_interface import FileInterface


class GamesMigrator:
    # Change game owner
    __UID = '0748-acc5-4c08-f229'
    __NAME = 'lol'
    __TAG = '7436'

    def __init__(self):
        self.__results = []

    def start(self):
        self.__create_user_storage_structure()
        return self.__results

    def __create_user_storage_structure(self):
        """ Create user and game structure """
        # Prepare user and languages
        user = self.__get_or_cr_user()
        lang_orig = self.__russian_lang_id()
        lang_tr = self.__english_lang_id()
        # Create BSFG game
        game_bsfg_props = {'name': f'BSFG', 'icon_chars': 'Bg', 'owner': user, 'lang_orig_id': lang_orig, }
        game_bsfg = Project.objects.create(**game_bsfg_props)
        game_bsfg.translate_to.set([lang_tr])
        self.__results += ['Migration status for game - BSFG', '=============' * 5]
        # HELIOS folder
        folder_helios = Folder.objects.create(project=game_bsfg, name='helios', position=1)
        helios_destination = self.__folder_path_from_instance(folder_helios)
        helios_source = os.path.join(settings.MEDIA_ROOT, 'cfg')
        helios_migrator = _MigratorIterator(int(folder_helios.id), lang_orig, lang_tr)
        helios_migrator.start_parsing(helios_source, helios_destination)
        self.__results.append(helios_migrator.stats)
        # HTML folder
        folder_html = Folder.objects.create(project=game_bsfg, name='html', position=2)
        html_destination = self.__folder_path_from_instance(folder_html)
        html_source = os.path.join(settings.MEDIA_ROOT, 'html')
        html_migrator = _MigratorIterator(int(folder_html.id), lang_orig, lang_tr)
        html_migrator.start_parsing(html_source, html_destination)
        self.__results.append(html_migrator.stats)
        # SCRIPTS folder
        folder_scripts = Folder.objects.create(project=game_bsfg, name='scripts', position=3)
        scripts_destination = self.__folder_path_from_instance(folder_scripts)
        scripts_source = os.path.join(settings.MEDIA_ROOT, 'scripts')
        scripts_migrator = _MigratorIterator(int(folder_scripts.id), lang_orig, lang_tr)
        scripts_migrator.start_parsing(scripts_source, scripts_destination)
        self.__results.append(scripts_migrator.stats)
        # Create Line Strike game
        game_ls_props = {'name': f'Line Strike', 'icon_chars': 'Ls', 'owner': user, 'lang_orig_id': lang_orig, }
        game_ls = Project.objects.create(**game_ls_props)
        game_ls.translate_to.set([lang_tr])
        self.__results += ['Migration status for game - Line Strike', '=============' * 5]
        # FILES folder (it's a random name)
        folder_ls = Folder.objects.create(project=game_ls, name='files', position=1)
        ls_destination = self.__folder_path_from_instance(folder_ls)
        ls_source = os.path.join(settings.MEDIA_ROOT, 'ls')
        ls_migrator = _MigratorIterator(int(folder_ls.id), lang_orig, lang_tr)
        ls_migrator.start_parsing(ls_source, ls_destination)
        self.__results.append(ls_migrator.stats)

    def __get_or_cr_user(self):
        nick = f'{self.__NAME}#{self.__TAG}'
        owner = {'username': self.__UID, 'email': None, 'password': self.__NAME, 'first_name': nick, 'last_name': 'ru'}
        try:
            return User.objects.get(username=self.__UID)
        except ObjectDoesNotExist:
            user = User.objects.create_user(**owner)
            creator = Permission.objects.get(codename='creator')
            user.user_permissions.add(creator)
            return user

    @staticmethod
    def __english_lang_id():
        english = Language.objects.get(name__iexact='english')
        return english.id

    @staticmethod
    def __russian_lang_id():
        russian = Language.objects.get(name__iexact='russian')
        return russian.id

    @staticmethod
    def __folder_path_from_instance(instance):
        """ Path of folder - users/<user_id>/<prj_id>/<folder_id> """
        _suffix = '{}/{}/{}'.format(instance.project.owner.id, instance.project.id, instance.id)
        return os.path.join(settings.MEDIA_ROOT, _suffix)


class _MigratorIterator:
    def __init__(self, folder_id: int, orig_id: int, tr_id: int):
        self.__folder_id = folder_id
        self.__lang_orig_id = orig_id  # Const 75
        self.__lang_tr_id = tr_id   # Const 18
        self.__path_source_orig = ''
        self.__path_source_tr = ''
        self.__path_source_tr_tmp = os.path.join(settings.MEDIA_ROOT, 'errors')  # Const ../users/errors
        self.__file_list_orig = []
        self.__file_list_tr = []
        self.__not_found_tr_list = []
        self.__stats = {'begin_orig': 0, 'begin_tr': 0, 'end_orig': 0, 'end_tr': 0}

    @property
    def stats(self) -> list:
        start_orig = self.__stats['begin_orig']
        start_tr = self.__stats['begin_tr']
        end_orig = self.__stats['end_orig']
        end_tr = self.__stats['end_tr']
        return [
            '=============' * 5,
            f'Parsed {start_orig + start_tr} files from {self.__path_source_orig} to Folder id:{self.__folder_id}',
            f'Originals: {start_orig}',
            f'Translates: {start_tr}',
            f'Success originals: {end_orig}',
            f'Success translates: {end_tr}',
            f'Not found translates: {len(self.__not_found_tr_list)}',
            'Not found translates for files:'
        ] + [f'     {file_name}' for file_name in self.__not_found_tr_list]

    def start_parsing(self, source: str, dst: str):
        self.__path_source_orig = os.path.join(source, 'ru')
        self.__path_source_tr = os.path.join(source, 'en')
        self.__file_list_orig = os.listdir(self.__path_source_orig)
        self.__file_list_tr = os.listdir(self.__path_source_tr)
        self.__stats = {
            'begin_orig': len(self.__file_list_orig),
            'begin_tr': len(self.__file_list_tr),
            'end_orig': 0,
            'end_tr': 0
        }
        self.__iterate_source_folder(dst)
        shutil.rmtree(source)

    def __iterate_source_folder(self, path_dst):
        for file_name in self.__file_list_orig:
            path_orig_old = os.path.join(self.__path_source_orig, file_name)
            if os.path.isfile(path_orig_old):
                # Move original file to users folder
                path_orig_new = self.__move_file(path_orig_old, path_dst)
                self.__parse_file_and_copy(file_name, path_orig_new)

    def __parse_file_and_copy(self, file_name, file_path):
        # Create file object
        file_obj = File.objects.create(
            name=file_name,
            folder_id=self.__folder_id,
            lang_orig_id=self.__lang_orig_id,
            data=file_path
        )
        file_manager = FileInterface(file_obj.id)
        file_manager.file_new(file_path, self.__lang_orig_id)
        self.__stats['end_orig'] += 1
        if file_name in self.__file_list_tr:
            path_tr_old = os.path.join(self.__path_source_tr, file_name)
            if os.path.isfile(path_tr_old):
                # Move original tr file to error folder (tmp)
                path_tr_new = self.__move_file(path_tr_old, self.__path_source_tr_tmp)
                file_manager.file_refresh(path_tr_new, self.__lang_tr_id, False)
                self.__stats['end_tr'] += 1
                return  # translate file found
        self.__not_found_tr_list.append(file_name)

    @staticmethod
    def __move_file(source_path, dst_dir):
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        return shutil.move(source_path, dst_dir)

