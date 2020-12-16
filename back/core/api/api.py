import logging
import os

from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from core.api.serializers import TransferFileSerializer, TranslatesSerializer
from core.services.file_interface.file_interface import FileInterface
from core.tasks import file_uploaded_new, file_uploaded_refresh
from core.models import File, Folder, Translated

logger = logging.getLogger('django')


class DefaultSetPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_query_param = 'page'
    page_size_query_param = 'size'
    last_page_strings = 'last'
    template = None


class ApiUtil:
    """ Class with static methods to help with API (qs - QuerySet, tr - Translates) """
    @staticmethod
    def qs_tr_filter_and_order(queryset: QuerySet, lang_id: int, search_text: str) -> QuerySet:
        """ Filter translates that have text to selected language and search text (!Care - method change income qs) """
        if lang_id and int(lang_id) > 0:
            queryset = queryset.filter(markitem__translate__language=lang_id,
                                       markitem__translate__text__exact='').distinct('fid')
        if search_text:
            search_vector = SearchVector('search_words', 'id')
            search_query = SearchQuery('')
            for word in search_text.split(' '):
                search_query &= SearchQuery(word)
            search_rank = SearchRank(search_vector, search_query)
            queryset = queryset.annotate(rank=search_rank).order_by('-rank')
        return queryset

    @staticmethod
    def file_upload_then_update_tr(file_id: int, lang_id: int, data) -> tuple[dict[str, str], int]:
        """ Refresh translates for uploaded (by user) file. If language is original - rebuild. """
        lang_id = int(lang_id)  # Used in == expressions
        try:
            _file_object = File.objects.select_related('lang_orig').get(id=file_id)
            _file_lang_orig_id: int = _file_object.lang_orig.id
        except ObjectDoesNotExist:
            logger.warning(f'File to update not found id:{file_id}')
            return {'err': 'file to update not found'}, status.HTTP_404_NOT_FOUND
        else:  # Save on IO to safe send to Celery
            _is_original: bool = lang_id == _file_lang_orig_id  # Check here for optimisation
            if _is_original:  # Replace original file
                # FIXME - if file linked with repo - disable upload
                _file_object.data.delete()
                _file_object.data = data
                _file_object.save()
                _tmp_path: str = _file_object.data.path  # FIXME: path not same as name
            else:  # Write new file to disk
                # If file left in error storage - it's an error :) -> tmp file(copy only) deleted after finish
                _name = f'{file_id}_{lang_id}.txt'
                settings.STORAGE_ERRORS.save(_name, data)
                _tmp_path = settings.STORAGE_ERRORS.path(_name)
        logger.info(f'Celery task - File:{file_id} refresh translates from {_tmp_path} for language:{lang_id}')
        file_uploaded_refresh.delay(file_id, lang_id, _tmp_path, _is_original)
        return {'ok': 'file build for language'}, status.HTTP_200_OK

    @staticmethod
    def file_new(folder_id: int, file_name: str, data) -> tuple[dict[str, any], int]:
        """ After user upload new file - run Celery task to build translates """
        try:
            _folder = Folder.objects.select_related('project__lang_orig').get(id=folder_id)
        except ObjectDoesNotExist:
            logger.warning(f'Create file error: file folder:{folder_id} not found')
            return {'err': 'folder not found'}, status.HTTP_404_NOT_FOUND
        # Create file object
        _prj_lang_orig_id: int = _folder.project.lang_orig.id
        _serializer = TransferFileSerializer(data={
            'name': file_name,
            'folder': folder_id,
            'lang_orig': _prj_lang_orig_id,  # TODO: Can be set by user
            'data': data,
        })
        if _serializer.is_valid():
            _file_obj = _serializer.save()
            # Run celery parse delay task
            logger.info(f'File object created ID: {_file_obj.id}. Sending parse task to Celery.')
            file_uploaded_new.delay(_file_obj.id, _prj_lang_orig_id, _file_obj.data.path)
            return _serializer.data, status.HTTP_201_CREATED
        logger.warning(f'Error creating file object: {_serializer.errors}')
        return _serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def get_copy_filename_or_error(copy_id: int) -> tuple[any, int]:
        """ Return filename or error message and response status """
        try:
            # progress = Translated.objects.get(file_id=pk, language_id=lang_id)   <-- retrieve by fileID and langID
            _progress = Translated.objects.select_related('language', 'file').get(id=copy_id)
        except ObjectDoesNotExist:
            return 'file not found', status.HTTP_404_NOT_FOUND
        _file_path: str = _progress.translate_copy.path
        if _file_path:
            if os.path.exists(_file_path):
                _file_name: str = os.path.basename(_file_path)
                return {'name': _file_name, 'path': _file_path}, status.HTTP_200_OK
            else:
                logger.critical(f'Translate copy not found:{_file_path} but exist in data base')
                _msg = f'File {_progress.file.name} translated to {_progress.language.name} not found'
                return _msg, status.HTTP_406_NOT_ACCEPTABLE
        _msg = f'For file {_progress.file.name} translate to {_progress.language.name} not done'
        return _msg, status.HTTP_204_NO_CONTENT

    @staticmethod
    def translator_update_tr(file_id: int, request) -> tuple[dict[str, any], int]:
        """ Update translate and set flag to file to refresh copy when Celery run periodic update """
        try:
            _file_manager = FileInterface(file_id)
        except AssertionError:
            return {'err': 'file object error'}, status.HTTP_404_NOT_FOUND
        _tr_or_error, _status = _file_manager.translate_change_by_user(request.user.id, **request.data)
        if _status > 399:  # 400+ error codes
            return _tr_or_error, _status
        serializer = TranslatesSerializer(_tr_or_error, many=False)
        return serializer.data, _status
