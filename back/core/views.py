import logging

from django.http import FileResponse
from django.db.models import Max
from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Language, Project, Folder, FolderRepo, File, FileMark, ProjectPermission, TranslateChangeLog
from core.tasks import folder_update_repo_after_url_change, folder_repo_change_access_and_update, delete_from_os
from core.api.api import ApiUtil, DefaultSetPagination
from core.api.permisions import IsProjectOwnerOrReadOnly, IsProjectOwnerOrAdmin, IsProjectOwnerOrManage, \
    IsFileOwnerOrHaveAccess, IsFileOwnerOrTranslator, IsFileOwnerOrManager
from core.api.serializers import ProjectSerializer, FoldersSerializer, LanguagesSerializer, FilesSerializer, \
    FileMarksSerializer, PermissionsSerializer, FolderRepoSerializer, PermsListSerializer, TranslatesLogSerializer

logger = logging.getLogger('django')


# TODO: ORDERING !!!


class LanguageViewSet(viewsets.ModelViewSet):
    """ Display all languages on login """
    serializer_class = LanguagesSerializer
    http_method_names = ['get']
    queryset = Language.objects.filter(active=True)


class ProjectViewSet(viewsets.ModelViewSet):
    """ Project manager view. Only for owner. """
    serializer_class = ProjectSerializer
    lookup_field = 'save_id'
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]
    # ordering = ['-created']
    queryset = Project.objects.all()

    def get_queryset(self):
        """ Get projects that user have permissions """
        if self.request.user.has_perm('core.creator'):
            return self.request.user.project_set.all()
        return self.queryset.filter(projectpermission__user=self.request.user).distinct()

    def perform_create(self, serializer):
        _user = self.request.user
        _project_name: str = self.request.data.get("name")  # For log only
        logger.info(f'User {_user.first_name}:{_user.id} creating new project {_project_name}')
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        """ Call celery task to delete """
        _path: str = '{}/{}/'.format(instance.owner.id, instance.id)
        logger.info(f'Project delete model object:{instance.id} and dir in OS:{_path}')
        delete_from_os.delay('project', _path)
        instance.delete()


class ProjectPermsViewSet(viewsets.ModelViewSet):
    """ Project permission manager """
    serializer_class = PermissionsSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated, IsProjectOwnerOrAdmin]
    queryset = ProjectPermission.objects.all()

    def list(self, request, *args, **kwargs):
        _save_id: str = self.request.query_params.get('save_id')
        _qs = User.objects.filter(projectpermission__project__save_id=_save_id).distinct()
        _serializer = PermsListSerializer(_qs, many=True, context={'save_id': _save_id})
        return Response(_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # TODO: Check perms if 5 - can create 0, if 9 can create other
        _save_id: str = self.request.data.get('save_id')
        _first_name: str = self.request.data.get('first_name')
        _permission: int = self.request.data.get("permission")  # For log only
        _project = get_object_or_404(Project, save_id=_save_id)
        _user = get_object_or_404(User, first_name=_first_name)
        _log_tuple: tuple = (self.request.user.first_name, _permission, _first_name, _save_id)  # For log only
        logger.info('User {} give permission {} to other user {} for project {}'.format(*_log_tuple))
        serializer.save(project=_project, user=_user)


# Folder ViewSet
class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FoldersSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrManage]
    queryset = Folder.objects.all()

    def list(self, request, *args, **kwargs):
        _save_id: str = request.query_params.get('save_id')
        _qs = self.get_queryset().filter(project__save_id=_save_id)
        _serializer = self.get_serializer(_qs, many=True)
        return Response(_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """ Increment position when creating new folder """
        _save_id = self.request.data.get('save_id')
        # _project = Project.objects.get(save_id=_save_id)  # Project exist check in perms
        _project = get_object_or_404(Project, save_id=_save_id)
        _position = self.get_queryset().aggregate(m=Max('position')).get('m') or 0
        logger.info(f'User {self.request.user.first_name} creating new folder in project {_save_id}')
        serializer.save(project=_project, position=_position + 1)

    def update(self, request, *args, **kwargs):
        """ Check changing repository on update. If updated - update """
        # TODO: check position change
        _folder_instance = self.get_object()
        _repo_url: str = request.data.get('repo_url')
        _need_update: bool = _repo_url != _folder_instance.repo_url  # Repository URL have been changed
        _serializer = self.get_serializer(_folder_instance, data=request.data)
        _serializer.is_valid(raise_exception=True)  # Code: 400
        self.perform_update(_serializer)
        if _need_update:  # Run celery task to check folder in repository and update files if needed
            folder_update_repo_after_url_change.delay(_folder_instance.id)
        return Response(_serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        """ Call celery task to delete """
        _path: str = '{}/{}/{}/'.format(instance.project.owner.id, instance.project.id, instance.id)
        logger.info(f'Folder delete model object:{instance.id} and dir in OS:{_path}')
        delete_from_os.delay('folder', _path)
        instance.delete()


class FolderRepoViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = FolderRepoSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrManage]
    queryset = FolderRepo.objects.all()

    def update(self, request, *args, **kwargs):
        """ Update access to git repository """
        _folder_id: int = self.get_object().folder_id
        _access_type: str = request.data.get('type')
        _access_value = request.data.get('code')  # TODO - set type
        if _access_type and _access_value:
            # Run celery task to check access for repository and update files if needed
            folder_repo_change_access_and_update.delay(_folder_id, _access_type.lower(), _access_value)
            return Response({'status': 'updating', 'err': None}, status=status.HTTP_200_OK)
        return Response({'err': 'request params error'}, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FilesSerializer
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticated, IsFileOwnerOrHaveAccess]
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['name']
    # ordering_fields = ['error', 'warning', 'created']
    # ordering = ['-error', '-warning', '-created']
    pagination_class = DefaultSetPagination
    queryset = File.objects.all()

    def list(self, request, *args, **kwargs):
        """ Filter files with pagination """
        _folder_id: int = request.query_params.get('folder_id')
        if _folder_id:
            _qs = self.get_queryset().filter(folder_id=_folder_id)
        else:  # For translator only - files with translates
            _save_id: str = request.query_params.get('save_id')
            _qs = self.get_queryset().filter(folder__project__save_id=_save_id, error__exact="")
        _page = self.paginate_queryset(_qs.order_by('-error', '-warning', '-created'))  # TODO: Ordering filter
        _serializer = self.get_serializer(_page, many=True)
        return self.get_paginated_response(data=_serializer.data)

    def perform_destroy(self, instance):
        """ Call celery task to delete """
        _path: str = instance.data.path
        logger.info(f'File delete model object:{instance.id} and in OS:{_path}')
        delete_from_os.delay('file', _path)
        instance.delete()


class FileMarksView(viewsets.ModelViewSet):
    serializer_class = FileMarksSerializer
    http_method_names = ['get', 'put', 'post']
    permission_classes = [IsAuthenticated, IsFileOwnerOrTranslator]
    pagination_class = DefaultSetPagination
    queryset = FileMark.objects.all()

    def list(self, request, *args, **kwargs):
        """ Translate with pagination """
        _file_id: int = request.query_params.get('file_id')
        _no_trans: int = request.query_params.get('no_trans')  # exclude marks that have translates to no_trans lang
        _search_text: str = request.query_params.get('search_text')  # filter by text

        _queryset = self.get_queryset().filter(file_id=_file_id).order_by('fid')
        _queryset = ApiUtil.qs_tr_filter_and_order(_queryset, _no_trans, _search_text)
        _page = self.paginate_queryset(_queryset)
        _serializer = self.get_serializer(_page, many=True)
        return self.get_paginated_response(data=_serializer.data)

    def create(self, request, *args, **kwargs):
        """ Update translate and mark file to refresh copy when Celery run periodic update """
        _file_id: int = request.data.get('file_id')
        _response, _status = ApiUtil.translator_update_tr(_file_id, request)
        return Response(_response, status=_status)


class TranslatesLogView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ To display translate change log when translate selected """
    serializer_class = TranslatesLogSerializer
    permission_classes = [IsAuthenticated, IsFileOwnerOrTranslator]
    queryset = TranslateChangeLog.objects.all().order_by('-created')

    def retrieve(self, request, *args, **kwargs):
        """ All changes for translate (pk) """
        _file_id: int = self.request.query_params.get('file_id')
        _qs = self.get_queryset().filter(translate_id=kwargs['pk'], translate__item__mark__file__id=_file_id)
        _serializer = self.get_serializer(_qs, many=True)
        return Response(_serializer.data)


class TransferFileView(viewsets.ViewSet):
    """ File transfer with user - Upload and Download files """
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsFileOwnerOrManager]

    def retrieve(self, request, pk=None):
        """ Return file to download by Translated.id (Can be changed/add to retrieve by File.id and Lang.id) """
        _data, _status = ApiUtil.get_copy_filename_or_error(pk)  # data can be str or AnyDataClass
        if _status == 200:
            # TODO: StreamingHttpResponse
            return FileResponse(open(_data['path'], 'rb'), as_attachment=True, filename=_data['name'])
        else:
            return Response({'err': _data}, status=_status)

    def create(self, request):
        """
            Upload file from user UI and run full 'build translates' progress:
                Folder ID and file name -> File new -> put in folder and rebuild
                File ID -> File not new:
                    Original language -> rebuild
                    Other language -> renew translate for selected language
        """
        _folder_id: int = request.data.get('folder_id')
        _file_name: str = request.data.get('name')
        _file_id: int = request.data.get('file_id')
        _lang_id: int = request.data.get('lang_id')
        _data = request.data.get('data')

        if not _data:  # TODO: mb allow to create if repository is set - to update from repo...
            _response, _status = {'err': 'upload file is empty or not set'}, status.HTTP_400_BAD_REQUEST
        elif _folder_id and _file_name and not _file_id:   # File is new
            _response, _status = ApiUtil.file_new(_folder_id, _file_name, _data)
        elif _lang_id:  # Upload translate file for language (can be original)
            _response, _status = ApiUtil.file_upload_then_update_tr(_file_id, _lang_id, _data)
        else:
            _response, _status = {'err': 'request params error'}, status.HTTP_400_BAD_REQUEST
        return Response(_response, status=_status)
