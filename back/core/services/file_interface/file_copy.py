import logging

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
