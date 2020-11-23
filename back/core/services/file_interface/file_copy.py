class CopyContextControl:
    """ Handle creation of file copy. Current value can be changed at any time """
    def __init__(self, path, codec, mode='newline'):
        assert isinstance(path, str), "Path of copy must be type str"
        self.__path = path
        self.__codec = codec
        self.__mode = mode
        self.__unsaved = ''
        self.__current = ''
        self.__filo = open(path, 'w', encoding=codec)

    def add_data(self, value):
        data = value if self.__mode == 'append' else value + '\n'
        self.__unsaved += self.__current
        self.__current = data

    def replace_and_save(self, value):
        data = value if self.__mode == 'append' else value + '\n'
        # Write data only on replace - for less amount off disk writes
        self.__save_write(data)
        # Null delta content
        self.__current = ''
        self.__unsaved = ''

    def finish(self):
        """ Write left unsaved data """
        self.__save_write('')
        self.__filo.close()

    def __save_write(self, data):
        # FIXME: make normal file save system
        try:
            self.__filo.write(self.__unsaved + data)
        except UnicodeEncodeError:
            # TODO: log error -> can't save lang:<id> to original file codec:<codec>
            self.__filo.write(self.__unsaved + self.__current)
        except ValueError:
            self.__filo = open(self.__path, 'a', encoding=self.__codec)
            self.__filo.write(self.__unsaved + data)
