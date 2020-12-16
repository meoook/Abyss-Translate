from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core.models import Translate

from core.services.file_interface.file_model_api import FileModelApi
from core.services.file_interface.file_related_model import FileRelatedModelApi


class FileInterface(FileModelApi):
    """ File API to work with file object in application (os and model) """

    def __init__(self, file_id: int):
        """ Get file object from database to do other actions """
        super().__init__(file_id)

    def file_new(self, file_path: str, original_lang_id: int) -> None:
        """ When new file -> update from repo -> get info -> parse -> cr progress """
        try:
            self._file_download_from_repo()
            self.file_refresh(file_path, original_lang_id, True)
        except AssertionError:
            self._log_err(f'error loading file {file_path}')

    def file_refresh(self, tmp_path: str, lang_id: int, is_original=False):
        if not self._file_refresh(tmp_path, lang_id, is_original) and is_original:  # Don't change expressions order
            self._save_error_file()

    def file_refresh_original(self):
        """ After git upload file - need to refresh it """
        self.file_refresh(tmp_path=self._file.data.path, lang_id=self._file.lang_orig, is_original=True)

    def translate_change_by_user(self, translator_id, trans_id, text, md5sum=None, **_kwargs) -> tuple[dict, int]:
        """ Create or update translate(s) and return status code with Translate object or error data !named params! """
        if not trans_id or not translator_id:
            self._log_err("request params error")
            return {'err': 'request params error'}, status.HTTP_400_BAD_REQUEST
        try:
            _translate = Translate.objects.get(id=trans_id)
        except ObjectDoesNotExist:
            return {'err': 'translate not found'}, status.HTTP_404_NOT_FOUND
        # Can't change original text
        _translate_lang_id = _translate.language.id
        if _translate_lang_id == self._file.lang_orig.id:
            return {'err': 'can\'t change original text'}, status.HTTP_400_BAD_REQUEST
        _model_api = FileRelatedModelApi()
        if md5sum:  # multi update
            _filter_options = {'item__mark__file': self._file, 'language': _translate_lang_id, 'item__md5sum': md5sum}
            for translate_obj in Translate.objects.filter(**_filter_options):
                _model_api.translate_change_by_user(translate_obj, text=text, user_id=translator_id)
        else:
            _model_api.translate_change_by_user(_translate, text=text, user_id=translator_id)
        self._file_progress_refresh(lang_id=_translate_lang_id)
        return _translate, status.HTTP_201_CREATED

    def translated_copy_refresh(self, lang_to_id: int) -> None:
        """ Create or update translated copy - then update it in repo """
        self._translate_copy_create(lang_to_id)
        self._translate_copy_upload_in_repo(lang_to_id)
