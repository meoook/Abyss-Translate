import os
import logging

from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status, filters
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Max, Q
from django.core.exceptions import ObjectDoesNotExist

from django.http import FileResponse

from .serializers import ProjectSerializer, FoldersSerializer, LanguagesSerializer, FilesSerializer, \
    TransferFileSerializer, FileMarksSerializer, PermissionsSerializer, TranslatesSerializer, FolderRepoSerializer, \
    PermsListSerializer
from .models import Languages, Projects, Folders, FolderRepo, Files, Translated, FileMarks, ProjectPermissions
from .services.file_manager import LocalizeFileManager
from .tasks import file_parse_uploaded, file_create_translated, folder_update_repo_after_url_change, \
    folder_repo_change_access_and_update
from .permisions import IsProjectOwnerOrReadOnly, IsProjectOwnerOrAdmin, IsProjectOwnerOrManage, \
    IsFileOwnerOrHaveAccess, IsFileOwnerOrTranslator, IsFileOwnerOrManager

logger = logging.getLogger('django')


# TODO: ORDERING !!!


class DefaultSetPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_query_param = 'page'
    page_size_query_param = 'size'
    last_page_strings = 'last'
    template = None


class LanguageViewSet(viewsets.ModelViewSet):
    """ Display all languages on login """
    serializer_class = LanguagesSerializer
    http_method_names = ['get']
    queryset = Languages.objects.filter(active=True)


class ProjectViewSet(viewsets.ModelViewSet):
    """ Project manager view. Only for owner. """
    serializer_class = ProjectSerializer
    lookup_field = 'save_id'
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]
    # ordering = ['-created']
    queryset = Projects.objects.all()

    def get_queryset(self):
        """ Get projects that user have permissions """
        if self.request.user.has_perm('core.creator'):
            return self.request.user.projects_set.all()
        return self.queryset.filter(projectpermissions__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def perform_destroy(self, instance):   # TODO: this
    #     """ call celery task to delete """
    #     pass


class ProjectPermsViewSet(viewsets.ModelViewSet):
    """ Project permission manager """
    serializer_class = PermissionsSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated, IsProjectOwnerOrAdmin]
    queryset = ProjectPermissions.objects.all()

    def list(self, request, *args, **kwargs):
        save_id = self.request.query_params.get('save_id')
        qs = User.objects.filter(projectpermissions__project__save_id=save_id).distinct()
        serializer = PermsListSerializer(qs, many=True, context={'save_id': save_id})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # TODO: Check perms if 5 - can create 0, if 9 can create other
        project = get_object_or_404(Projects, save_id=self.request.data.get('save_id'))
        user = get_object_or_404(User, username=self.request.data.get('username'))
        serializer.save(project=project, user=user)


# Folder ViewSet
class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FoldersSerializer
    # http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsAuthenticated, IsProjectOwnerOrManage]
    queryset = Folders.objects.all()

    def list(self, request, *args, **kwargs):
        save_id = request.query_params.get('save_id')
        qs = self.get_queryset().filter(project__save_id=save_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        project = Projects.objects.get(save_id=self.request.data.get('save_id'))  # Project exist check in perms
        position = self.get_queryset().aggregate(m=Max('position')).get('m') or 0
        serializer.save(project=project, position=position + 1)

    # def create(self, request, *args, **kwargs):
    #     """ Increment position. ID is hidden from users - using save_id """
    #     project = Projects.objects.get(save_id=request.data.get('save_id'))   # Project exist check in perms
    #     position = self.get_queryset().aggregate(m=Max('position')).get('m') or 0
    #     serializer = self.get_serializer(data={**request.data, 'project': project.id})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(position=position + 1)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ Check changing repository on update. If updated - update """
        folder_instance = self.get_object()
        repo_url = request.data.get('repo_url')
        need_update = repo_url != folder_instance.repo_url  # Repository URL have been changed
        serializer = self.get_serializer(folder_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if need_update:  # Run celery task to check folder in repository and update files if needed
            folder_update_repo_after_url_change.delay(folder_instance.id)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def perform_destroy(self, instance):   # TODO: this
    #     """ call celery task to delete """
    #     pass


class FolderRepoViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        # mixins.UpdateModelMixin,
                        # mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = FolderRepoSerializer
    # http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated, IsProjectOwnerOrManage]
    queryset = FolderRepo.objects.all()

    def create(self, request, *args, **kwargs):
        """ Update access to git repository """
        folder_id = request.data.get('folder_id')
        get_object_or_404(FolderRepo, folder_id=folder_id)  # Check exist status
        access_type = request.data.get('type')
        access_value = request.data.get('code')
        if access_type and access_value:
            # Run celery task to check folder in repository and update files if needed
            folder_repo_change_access_and_update.delay(folder_id, access_type.lower(), access_value)
            return Response({'status': 'updating', 'err': None}, status=status.HTTP_200_OK)
        return Response({'err': 'request params error'}, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FilesSerializer
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticated, IsFileOwnerOrHaveAccess]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created', 'state']
    ordering = ['state', '-created']
    pagination_class = DefaultSetPagination
    queryset = Files.objects.all()

    # def get_serializer_class(self):
    #     if self.request.user.has_perm('core.translator'):
    #         return FilesDisplaySerializer
    #     return FilesSerializer

    def list(self, request, *args, **kwargs):
        """ Filter files with pagination """
        folder_id = request.query_params.get('folder_id')
        if request.user.has_perm('core.creator'):
            qs = self.get_queryset().filter(folder_id=folder_id)
        elif folder_id:
            qs = self.get_queryset().filter(folder_id=folder_id)
        else:
            save_id = request.query_params.get('save_id')
            qs = self.get_queryset().filter(folder__project__save_id=save_id, state=2)
        page = self.paginate_queryset(qs.order_by('state', '-created'))  # TODO: Ordering filter
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    # def perform_destroy(self, instance):  # TODO: this
    #     """ call celery task to delete """
    #     pass


class FileMarksView(viewsets.ModelViewSet):
    serializer_class = FileMarksSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated, IsFileOwnerOrTranslator]
    pagination_class = DefaultSetPagination
    queryset = FileMarks.objects.all()

    def list(self, request, *args, **kwargs):
        """ Translates with pagination """
        file_id = request.query_params.get('file_id')
        distinct = request.query_params.get('distinct')
        no_trans = request.query_params.get('no_trans')  # exclude marks that have translates to no_trans lang
        # FIXME: mb other issue to save order
        # Entry.objects.order_by(Coalesce('summary', 'headline').desc())
        if distinct == 'true':
            qs_to_list = list(self.get_queryset().filter(file_id=file_id).values('md5sum', 'id').distinct('md5sum'))
            unique_md5_id_arr = [x['id'] for x in qs_to_list]
            queryset = self.get_queryset().filter(pk__in=unique_md5_id_arr).order_by('mark_number', 'col_number')
        else:
            queryset = self.get_queryset().filter(file_id=file_id).order_by('mark_number', 'col_number')
        if no_trans and int(no_trans) > 0:
            to_filter = queryset.filter(Q(translates__language=no_trans), ~Q(translates__text__exact=''))
            queryset = queryset.exclude(id__in=to_filter)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """ Create or update translates. Update translate progress. If finished - create translate file. """
        file_id = request.data.get('file_id')
        lang_id = request.data.get('lang_id')
        file_manager = LocalizeFileManager(file_id)
        if file_manager.error:
            return Response(file_manager.error, status=status.HTTP_404_NOT_FOUND)
        resp, sts = file_manager.create_mark_translate(request.user.id, **request.data)
        if sts > 399:  # 400+ error codes
            return Response(resp, status=sts)
        if file_manager.update_language_progress(lang_id):
            # Run celery task - create_translated_copy
            file_create_translated.delay(file_id, lang_id)
        serializer = TranslatesSerializer(resp, many=False)
        return Response(serializer.data, status=sts)


class TransferFileView(viewsets.ViewSet):
    """ FILE TRANSFER VIEW: Upload/Download files """
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsFileOwnerOrManager]

    def retrieve(self, request, pk=None):
        """ Return file to download by Translated.id (Can be changed to retrieve by File.id and Lang.id) """
        try:
            # progress = Translated.objects.get(file_id=pk, language_id=lang_id)   <-- retrieve by fileID and langID
            progress = Translated.objects.select_related('language', 'file').get(id=pk)
        except ObjectDoesNotExist:
            return Response({'err': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        if progress.finished:
            file_path = progress.translate_copy.path
            if os.path.exists(file_path):
                # TODO: StreamingHttpResponse
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
            return Response({'err': f'File {progress.file.name} translated to {progress.language.name} not found'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'err': f'For file {progress.file.name} translate to {progress.language.name} not done'},
                        status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """ Create file git_obj and related translated progress after file download (uploaded by user) """
        folder_id = request.data.get('folder_id')
        folder = Folders.objects.select_related('project__lang_orig').get(id=folder_id)
        # Create file object
        lang_orig_id = folder.project.lang_orig.id
        serializer = TransferFileSerializer(data={
            'name': request.data.get('name'),
            'folder': folder_id,
            'lang_orig': lang_orig_id,
            'data': request.data.get('data'),
        })
        if serializer.is_valid():
            serializer.save()
            file_id = serializer.data.get('id')  # TODO: check this method
            # Run celery parse delay task
            logger.info(f'File object created ID: {file_id}. Sending parse task to celery.')
            file_parse_uploaded.delay(file_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f'Error creating file object: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
