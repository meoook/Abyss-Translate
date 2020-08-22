import os
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Max, Subquery, Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core import management
from django.http import FileResponse, HttpResponse, Http404

from core.serializers import ProjectSerializer, FoldersSerializer, LanguagesSerializer, FilesSerializer, TransferFileSerializer, TranslatesSerializer, FileMarksSerializer, PermissionsSerializer, FilesDisplaySerializer
from .models import Languages, Projects, Folders, FolderRepo, Files, Translated, FileMarks, Translates, ProjectPermissions
from .tasks import file_parse, upload_translated

from core.utils.git_manager import GitManage
from core.services.access_system_ import project_check_perm_or_404, folder_check_perm_or_404, file_check_perm_or_404
from core.services.translate_manage import translate_create

logger = logging.getLogger('django')

# TODO: CHECK USER RIGHTS/PERMISSIONS


class DefaultSetPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_query_param = 'p'
    page_size_query_param = 's'
    last_page_strings = 'last'
    template = None


class LanguageViewSet(viewsets.ModelViewSet):
    """ Display all languages on login """
    serializer_class = LanguagesSerializer
    http_method_names = ['get']
    queryset = Languages.objects.filter(active=True)


class FileMarksView(viewsets.ModelViewSet):
    serializer_class = FileMarksSerializer
    # http_method_names = ['get', 'post']
    pagination_class = DefaultSetPagination
    queryset = FileMarks.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """ Filter owner files """
        try:
            queryset = self.get_queryset().get(pk=kwargs['pk'], file__owner=request.user)
            serializer = self.get_serializer(queryset, many=False)
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response({'err': 'mark not found'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """ Translates with pagination """
        file_id = request.query_params.get('f')
        distinct = request.query_params.get('d')
        no_trans = request.query_params.get('nt')           # exclude marks that have translates to no_trans lang
        file_check_perm_or_404(file_id, request.user, 1)    # can translate or owner
        # FIXME: mb other issue to save order
        if distinct == 'true':
            uniq_md5_id_arr = [x['id'] for x in list(
                self.get_queryset().filter(file_id=file_id).values('md5sum', 'id').distinct('md5sum'))]
            queryset = self.get_queryset().filter(pk__in=uniq_md5_id_arr).order_by('mark_number', 'col_number')
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
        file_id = request.data.get('fileID')
        mark_id = request.data.get('markID')
        md5sum = request.data.get('md5')
        lang_trans = request.data.get('langID')
        text = request.data.get('text')     # TODO: Check mb can get in binary??
        file_check_perm_or_404(file_id, request.user, 1)    # can translate or owner
        return translate_create(file_id, mark_id, lang_trans, request.user.id, text, md5sum)


class TransferFileView(viewsets.ViewSet):
    """ FILE TRANSFER VIEW: Upload/Download files """
    parser_classes = (MultiPartParser, )
    serializer_class = TransferFileSerializer

    def retrieve(self, request, pk=None):
        """ Return file to download by Translated.id (Can be changed to retrieve by fileID and langID) """
        try:
            # progress = Translated.objects.get(file_id=pk, language_id=lang_id)   <-- retrieve by fileID and langID
            progress = Translated.objects.select_related('language', 'file').get(id=pk, file__owner=request.user)
        except ObjectDoesNotExist:
            return Response({'err': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        if progress.finished:
            file_path = progress.translate_copy.path
            if os.path.exists(file_path):
                # TODO: StreamingHttpResponse
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
            return Response({'err': f'File {progress.file.name} translated to {progress.language.name} not found'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'err': f'For file {progress.file.name} translate to {progress.language.name} not done'},
                        status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """ Create file obj and related translated progress after file download (uploaded by user) """
        folder_id = request.data.get('folder')
        folder_check_perm_or_404(folder_id, request.user, 8)  # Can manage
        folder = Folders.objects.select_related('project__lang_orig').get(id=folder_id)
        # Create file obejct
        lang_orig_id = folder.project.lang_orig.id
        serializer = self.get_serializer(data={
            'owner': request.user.id,
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
            file_parse.delay(file_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f'Error creating file object: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    """ Project manager view. Only for owner. """
    serializer_class = ProjectSerializer
    lookup_field = 'save_id'
    # ordering = ['position']
    queryset = Projects.objects.all()

    def get_object(self, pk=None):
        """ Can get only own projects """
        try:
            return self.request.user.projects_set.get(id=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_queryset(self):
        """ Get projects that user have permissions """
        user = self.request.user
        if user.has_perm('localize.creator'):
            return self.request.user.projects_set.all()
        return self.queryset.filter(project_permissions_user=user)

    def create(self, request, *args, **kwargs):
        """ Check if user have rights to create """
        if not self.request.user.has_perm('localize.creator'):
            return Response({'err': 'You have no permission to create projects'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectPermsViewSet(viewsets.ModelViewSet):
    """ Project permission manager """
    serializer_class = PermissionsSerializer
    http_method_names = ['get', 'post', 'delete']
    queryset = ProjectPermissions.objects.all()

    def get_queryset(self):
        if self.request.method == 'GET':
            save_id = self.request.query_params.get('project')
        save_id = self.request.data.get('project')
        project_check_perm_or_404(save_id, self.request.user, 9)    # Can manage roles
        return self.queryset.filter(project__save_id=save_id)


# Folder ViewSet
class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FoldersSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Folders.objects.all()

    def get_queryset(self):
        save_id = self.request.data['project']
        project_check_perm_or_404(save_id, self.request.user, 8)   # Can manage
        return self.queryset.filter(project__save_id=save_id)

    def create(self, request, *args, **kwargs):
        """ Increment position. ID is hidden from users - using save_id """
        save_id = request.data.get('project')
        project = Projects.objects.get(save_id=save_id)
        if not project:
            return Response({'err': 'project not found'}, status=status.HTTP_404_NOT_FOUND)
        position = self.get_queryset().aggregate(m=Max('position')).get('m') or 0
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(position=position + 1, project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ Check changing repository on update. If updated - update """
        folder_instance = self.get_object()
        repo_url = request.data.get('repository')

        serializer = self.get_serializer(folder_instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if repo_url != folder_instance.repository:   # Repository URL have been changed
            folder_files = Files.objects.filter(folder=folder_instance)
            if repo_url:    # Input URL not empty
                git_manager = GitManage()
                git_manager.check_url(repo_url)
                if git_manager.repo:   # URL parsed success
                    defaults = {**git_manager.repo, 'hash': git_manager.new_hash}
                    repo_obj, created = FolderRepo.objects.update_or_create(folder=folder_instance, defaults=defaults)
                    # repo_obj.error = git_manager.error
                else:
                    pass

                if git_manager.new_hash:  # Folder exist
                    folder_files.update(repo_founded=False, repo_hash=False)    # SET founded - false for all files

                    file_list = []
                    for filo in folder_files:
                        file_list.append({'id': filo.id, 'name': filo.name, 'hash': filo.repo_hash, 'path': filo.data.path})
                    updated_files = git_manager.update_files(file_list)
                    if updated_files:
                        for filo in updated_files:
                            Files.objects.filter(id=filo['id']).update(repo_founded=True, repo_hash=filo['hash'])
                            # FIXME: Get file info
                            management.call_command('file_rebuild', filo['id'])
                else:
                    folder_files.update(repo_founded=None, repo_hash=False)
            else:
                FolderRepo.objects.filter(folder=folder_instance).delete()
                folder_files.update(repo_founded=None, repo_hash=False)

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Folder ViewSet
class FileViewSet(viewsets.ModelViewSet):
    # serializer_class = FilesSerializer
    http_method_names = ['get', 'put', 'delete']
    pagination_class = DefaultSetPagination
    queryset = Files.objects.all().order_by('state', '-created')

    def get_serializer_class(self):
        if self.request.user.has_perm('localize.translator'):
            return FilesDisplaySerializer
        return FilesSerializer

    def get_queryset(self):
        """ Filter files for tranlator or search by name """
        search = self.request.query_params.get('search', None)
        qs = self.queryset.filter(name__icontains=search) if search else self.queryset
        return qs.filter(state=2) if self.request.user.has_perm('localize.translator') else qs

    def get_object(self, pk=None):
        """ Manage file by access """
        file_check_perm_or_404(pk, self.request.user, 8)  # Can manage
        return self.queryset.get(pk=pk)

    def list(self, request, *args, **kwargs):
        """ Filter files with pagination """
        if request.user.has_perm('localize.translator'):
            qs = self.get_queryset().filter(folder__project_save_id=request.query_params.get('save_id'))
        else:
            qs = self.get_queryset().filter(folder_id=request.query_params.get('folder'))
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
