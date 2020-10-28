
# defaults = {**self.__git.repo, 'sha': sha}
# FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)
import os

from core.services.file_interface.file_scanner import FileScanner

DATA_ANALYZERS = {
    'csv': {'reader': lambda x: f'csv_reader {x}', 'writer': 'csv_writer'},
    'html': {'reader': lambda x: f'html_reader {x}', 'writer': 'html_writer'},
    'ue': {'reader': lambda x: f'ue_reader {x}', 'writer': 'ue_writer'},
}


class FileDataInterface:
    """ Methods to works with file data (on hdd) """
    def __init__(self, method, options):
        self.__reader = DATA_ANALYZERS[method]['reader'](options)
        self.__writer = DATA_ANALYZERS[method]['writer']
        print('reader', self.__reader)

    def add_translations(self, language):
        pass

    def create_copy(self, language):
        pass

    def refresh(self):
        """ When file created or updated """
        pass


if __name__ == '__main__':
    scanned_amount = 0
    my_path = r'C:\Projects\PY\Abby\HELIOS'
    # my_path = r'C:\Projects\PY\Abby\HELIOS\ls'

    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if '-ru' in file_name or file_name == 'Ru.po':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            scanned_amount += 1
            # print(idxx, file_path, {**info.info})
            if not info.error:
                reader = FileDataInterface(info.method, info.options)
        else:
            # print(idxx, 'NO NEED TO CHECK', file_name)
            pass
        if scanned_amount > 3:
            print('FINISH')
            break
