class LocalizeFileReader:
    """ Read file by method and return mark by mark. Mark have array of items. """
    def __init__(self, f_path, f_codec, f_method, scan_options):
        assert isinstance(f_path, str), "Path parameter must be type - string"
        assert isinstance(f_codec, str), "Codec parameter must be type - string"
        assert f_method in ['csv', 'html', 'ue'], f'Parse method incorrect {f_method}'
        self.__path = f_path
        self.__codec = f_codec
        self.__method = f_method
        self.__options = scan_options

        self.__file_items = 0
        self.__file_marks = 0

        # Mark options
        self.__fid = None
        self.__words = 0
        self.__search_words = ''
        self.__context = ''
        self.__items = []  # Array of FileMarksObjects
        # Errors
        self.__error = None
        self.__warning = None

    def __iter__(self):
        return 'xx'

    def __next__(self):
        yield 'next xx'


# class FileMarkItem:
#     def __init__(self):
#         mark = models.ForeignKey(FileMark, on_delete=models.CASCADE)
#         item_number = models.PositiveIntegerField()  # Col for CSV
#         md5sum = models.CharField(max_length=32)  # Check same values
#         md5sum_clear = models.CharField(max_length=32)  # Help translate - MD5 without special chars or digits
#         words = models.PositiveIntegerField()
#
#         mark = models.ForeignKey(FileMark, on_delete=models.CASCADE)
#         language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
#         text = models.TextField()  # db_index=True
#         warning = models.CharField(max_length=255, blank=True)

