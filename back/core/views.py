import os
import logging
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Max, Subquery, Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core import management
from django.http import FileResponse, HttpResponse, Http404

from core.serializers import ProjectSerializer, FoldersSerializer, LanguagesSerializer,\
    FilesSerializer, TransferFileSerializer, TranslatesSerializer, FileMarksSerializer

from .models import Languages, Projects, Folders, FolderRepo, Files, Translated, FileMarks, Translates

from core.utils.get_data_info import GetDataInfo
from core.utils.git_manager import GitManage

from core.tasks import file_parse

logger = logging.getLogger('django')

# TODO: CHECK USER RIGHTS/PERMISSIONS


class DefaultSetPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_query_param = 'p'
    page_size_query_param = 's'
    last_page_strings = 'last'
    template = None


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
        no_trans = request.query_params.get('nt')
        try:
            file_obj = Files.objects.get(pk=file_id, owner=request.user)
        except ObjectDoesNotExist:
            return Response({'err': 'file not found'}, status=status.HTTP_404_NOT_FOUND)
        # FIXME: mb other issue
        if distinct == 'true':
            uniq_md5_id_arr = [x['id'] for x in list(
                self.get_queryset().filter(file=file_obj).values('md5sum', 'id').distinct('md5sum'))]
            queryset = self.get_queryset().filter(pk__in=uniq_md5_id_arr).order_by('mark_number', 'col_number')
        else:
            queryset = self.get_queryset().filter(file=file_obj).order_by('mark_number', 'col_number')
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
        lang_translate = request.data.get('langID')
        text = request.data.get('text')     # TODO: Check mb can get in binary??
        if file_id and mark_id and lang_translate:
            try:
                file_obj = Files.objects.get(pk=file_id, owner=request.user)
            except ObjectDoesNotExist:
                return Response({'err': 'file not found'}, status=status.HTTP_404_NOT_FOUND)
            # Check lang_translate in list of need translate languages
            if lang_translate not in file_obj.translate_to.values_list('id', flat=True):
                return Response({'err': "no need translate to this language"}, status=status.HTTP_400_BAD_REQUEST)
            # Can't change original text
            if lang_translate == file_obj.lang_orig.id:
                # TODO: permisions check - mb owner can change
                return Response({'err': "can't change original text"}, status=status.HTTP_404_NOT_FOUND)

            # Get or create translate(s)
            if md5sum:  # multi update
                # Check if translates exist with same md5
                translates = Translates.objects.filter(mark__file=file_obj, language=lang_translate, mark__md5sum=md5sum)
                control_marks = file_obj.filemarks_set.filter(md5sum=md5sum)
            else:
                translates = Translates.objects.filter(mark__file=file_obj, language=lang_translate, mark__id=mark_id)
                control_marks = file_obj.filemarks_set.filter(id=mark_id)
            # TODO: check text language and other
            translates.update(text=text)
            if translates.count() != control_marks.count():
                def_obj = {'translator': request.user, 'text': text, 'language_id': lang_translate}
                objs = [Translates(**def_obj, mark=mark) for mark in control_marks if mark.id not in translates.values_list('mark', flat=True)]
                Translates.objects.bulk_create(objs)

            return_trans = translates.get(mark_id=mark_id)
            serializer = TranslatesSerializer(return_trans, many=False)
            # Get file progress for language
            try:
                progress = Translated.objects.get(file=file_obj, language=lang_translate)
            except ObjectDoesNotExist:
                logger.error(f"For file {file_obj.id} related translated object not found: language {lang_translate}")
                return Response({'err': 'related translated object not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            how_much_translated = self.get_queryset().filter(Q(translates__language=lang_translate), Q(file=file_obj), ~Q(translates__text__exact='')).count()
            if file_obj.items == how_much_translated:
                progress.finished = True
                # FIXME: create file must be triggered by "file checked state or cron"
            elif file_obj.items < how_much_translated:
                logging.error(f'For file {file_obj.id} translates items more then file have')
                progress.finished = True    # But it's error
            elif progress.finished:
                progress.finished = False
            progress.items = how_much_translated
            progress.save()
            # print(f'File {file_obj.name}(id:{file_obj.id}) translated {round(how_much_translated / file_obj.items_count * 100)}%')
            if progress.finished:
                management.call_command('file_create_translated', file_obj.id, lang_translate)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'err': 'request params error'}, status=status.HTTP_400_BAD_REQUEST)


class TransferFileView(viewsets.ViewSet):
    """ FILE TRANSFER VIEW: Upload/Download files """
    parser_classes = (MultiPartParser, FileUploadParser)
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
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX START DATA')
        req_folder = request.data.get('folder')
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX X')
        # req_data = request.data.get('data')
        req_data = request.FILES['data']
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX XX')
        # TODO: Check user rights to create file
        try:    # TODO: Check need related lang_orig to get id
            folder = Folders.objects.select_related('project__lang_orig', 'project__translate_to').get(id=req_folder, project__owner=request.user)
        except ObjectDoesNotExist:
            return Response({'err': 'folder not found'}, status=status.HTTP_404_NOT_FOUND)

        lang_orig_id = folder.project.lang_orig.id
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX{lang_orig_id}')
        # Create file obejct
        serializer = self.serializer_class(data={
            'owner': request.user.id,
            'name': request.data.get('name'),
            'folder': folder.id,
            'lang_orig': lang_orig_id,
            'data': req_data,
        })
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX{2}')
        if serializer.is_valid():
            serializer.save()
            # Create related translated progress objects
            # print('XXXXXXXXXXXXXXXXXXXXXX', 33)
            file_id = serializer.data.get('id')  # TODO: check this method
            # translate_to_ids = folder.project.translate_to.values_list('id', flat=True)
            # objs = [Translated(file_id=serializer.data.get('id'), language_id=lang_id) for lang_id in translate_to_ids]
            # Translated.objects.bulk_create(objs)
            logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX{4}')

            # Run celery parse delay task
            file_parse.delay(file_id)
            logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX{45}')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response({'err': 'file already exist'}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f'XXXXXXXXXXXXXXXXXXXXXX{5}')


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LanguageViewSet(viewsets.ModelViewSet):
    """ Display all languages on login """
    serializer_class = LanguagesSerializer
    http_method_names = ['get']
    queryset = Languages.objects.filter(active=True)


class ProjectViewSet(viewsets.ModelViewSet):
    """ Project manager view. Only for owner. """
    serializer_class = ProjectSerializer
    lookup_field = 'save_id'
    # ordering = ['position']
    queryset = Projects.objects.all()

    def get_queryset(self):
        return self.request.user.projects_set.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def update(self, request, save_id=None, *args, **kwargs):
    #     project = self.get_object()  # by save_id -> lookup_field
    #     serializer = ProjectSerializer(project, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response('project not found', status=status.HTTP_404_NOT_FOUND)

    # def retrieve(self, request, save_id=None, *args, **kwargs):
    #     project = self.get_object()  # by save_id -> lookup_field
    #     serializer = ProjectSerializer(queryset)
    #     if serializer.is_valid():
    #         return Response(serializer.data)
    #     else:
    #         return Response('project not found', status=status.HTTP_404_NOT_FOUND)


# Folder ViewSet
class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FoldersSerializer
    http_method_names = ['post', 'put', 'delete']
    queryset = Folders.objects.all()

    def get_object(self):
        try:
            instance = self.get_queryset().get(id=self.kwargs['pk'], project__owner=self.request.user)
            return instance
        except Folders.DoesNotExist:
            raise Http404  # Response({'err': 'folder not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """ Increment position. ID is hidden from users - using save_id """
        project = Projects.objects.get(save_id=request.data['project'])
        if project:
            position = self.get_queryset().filter(project=project).aggregate(m=Max('position')).get('m') or 0
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(position=position + 1, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'err': 'fail to create folder'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'err': 'project not found'}, status=status.HTTP_404_NOT_FOUND)

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
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Folder ViewSet
class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FilesSerializer
    http_method_names = ['get', 'put', 'delete']
    pagination_class = DefaultSetPagination
    queryset = Files.objects.all()

    def get_queryset(self):
        """ Filter owner files """
        return self.queryset.filter(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """ Filter owner files """
        try:
            project = Projects.objects.get(folders__files=kwargs['pk'])
        except Projects.DoesNotExist:
            return Response({'err': 'project not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            instance = self.queryset.get(owner=request.user, pk=kwargs['pk'])
        except Files.DoesNotExist:
            return Response({'err': 'file not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, many=False)
        return Response({**serializer.data, 'translate_to': [x.id for x in project.translate_to.all()]})

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.name = request.data.get("name")
    #     instance.save()
    #
    #     serializer = self.get_serializer(instance)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """ Filter owner files with pagination """
        folder = request.query_params.get('f')
        if folder:
            # queryset = self.get_queryset().filter(folder_id=folder, owner=self.request.user).order_by('state', '-created')
            queryset = self.get_queryset().filter(folder_id=folder).order_by('state', '-created')
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(data=serializer.data)
        return Response({'err': 'folder not found'}, status=status.HTTP_404_NOT_FOUND)
        # raise APIException('folder not found') # CODE:500

