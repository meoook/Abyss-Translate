class CopyContextControl:
    """ Handle creation of file copy. Current value can be changed at any time """
    def __init__(self, path, codec, mode='newline'):
        assert isinstance(path, str), "Path of copy must be type str"
        self.__mode = mode
        self.__unsaved = ''
        self.__current = ''
        with open(path, 'w', encoding=codec) as filo:
            self.__filo = filo

    def add_data(self, value):
        data = value if self.__mode == 'append' else value + '\n'
        self.__unsaved += self.__current
        self.__current = data

    def replace_and_save(self, value):
        data = value if self.__mode == 'append' else value + '\n'
        self.__filo.write(self.__unsaved + data)    # Write data only on replace - for less amount off disk writes
        # Null delta content
        self.__current = ''
        self.__unsaved = ''
