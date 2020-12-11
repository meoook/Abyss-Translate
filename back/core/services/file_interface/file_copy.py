import logging
import os

logger = logging.getLogger('django')


class CopyContextControl:
    """ Handle creation of file translation copy. Current value can be changed/replaced at any time """
    def __init__(self, path: str, codec: str, mode: str = 'newline'):
        assert isinstance(path, str) and path, "Path of copy must be type str and not empty"
        self.__path = path
        self.__codec = codec
        self.__mode = mode  # Mode 'append' for html
        self.__unsaved = ''
        self.__current = ''
        logger.info(f'Creating/updating translation copy {path} in codec {codec}')
        self.__filo = open(path, 'w', encoding=codec)  # FIXME: not safe :(

    def add_data(self, value: str) -> None:
        data = value if self.__mode == 'append' else value + '\n'
        self.__unsaved += self.__current
        self.__current = data

    def replace_and_save(self, value: str) -> None:
        data = value if self.__mode == 'append' else value + '\n'
        # Write data only on replace - for less amount off disk writes
        self.__safe_write(data)
        # Null delta content
        self.__current = ''
        self.__unsaved = ''

    def finish(self) -> None:
        """ Write left unsaved data """
        self.__safe_write('')
        self.__filo.close()
        logger.info(f'Translation copy {self.__path} successfully created')

    def __safe_write(self, data: str) -> None:
        """ Reopen file if was closed """
        try:
            self.__filo.write(self.__unsaved + data)
        except UnicodeEncodeError:  # FIXME: b-logic change codec or error ?
            logger.warning(f'Can\'t write in {self.__path} - language error for codec:{self.__codec}')
            self.__filo.write(self.__unsaved + self.__current)
        except ValueError:
            logger.critical(f'File {self.__path} was unexceptionally closed. Reopen...')
            self.__filo = open(self.__path, 'a', encoding=self.__codec)
            self.__filo.write(self.__unsaved + data)

    @staticmethod
    def get_path(original_file_path: str, lang_short_name: str) -> str:
        """ To make method static (used without Class object) """
        _params = (original_file_path, lang_short_name)
        return CopyContextControl.get_path_in_folder(*_params) or CopyContextControl.get_path_with_suffix(*_params)

    @staticmethod
    def get_path_in_folder(original_file_path: str, lang_short_name: str) -> str:
        """ Get translate copy path in 'language short name' folder (create folder if needed) """
        base_dir_name = os.path.dirname(original_file_path)
        file_name = os.path.basename(original_file_path)
        lang_dir = os.path.join(base_dir_name, lang_short_name)

        if not os.path.exists(lang_dir):
            try:
                os.makedirs(lang_dir)
            except OSError:  # Return path in same folder
                return ''
        return os.path.join(base_dir_name, lang_short_name, file_name)

    @staticmethod
    def get_path_with_suffix(original_file_path: str, lang_short_name: str) -> str:
        """ Get translate copy path related to original but add 'language short name' suffix """
        dir_name = os.path.dirname(original_file_path)
        file_name = os.path.basename(original_file_path)
        name, ext = os.path.splitext(file_name)
        copy_name = f'{name}-{lang_short_name}{ext}'
        return os.path.join(dir_name, copy_name)
