import logging
from rest_framework import viewsets, mixins, status, permissions, filters
from django.db.models import Max, Subquery, Q
from django.core.exceptions import ObjectDoesNotExist

from .models import Languages, Projects, Folders, FolderRepo, Files, Translated, FileMarks, ProjectPermissions
from .services.file_manager import LocalizeFileManager

from core.services.git_manager import GitManage

logger = logging.getLogger('django')


class LocalizeFolderManager:

    def __init__(self, folder_id, *args, **kwargs):
        self.__id = folder_id

    def change_repo_url(self, repo_url):
        """ This func must be used when repo_url != folder.repo_url """
        folder_files = Files.objects.filter(folder_id=self.__id)
        if not repo_url:    # Input URL empty
            FolderRepo.objects.filter(folder_id=self.__id).delete()
            logger.info(f'Folder id:{self.__id} repo url set to empty - repo obj deleted')
            folder_files.update(repo_status=None, repo_hash='')
            logger.info(f'Changed repo status for files in folder id:{self.__id}')
            return True
        # Check folder and files from new repo URL
        git_manager = GitManage()
        if git_manager.check_url(repo_url):   # URL exist and have access to repo
            defaults = {**git_manager.repo, 'hash': git_manager.new_hash}
            repo_obj, created = FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)
            # repo_obj.error = git_manager.error
        else:
            pass

        if git_manager.new_hash:  # Folder exist
            folder_files.update(repo_status=False, repo_hash='')    # SET founded - false for all files

            file_list = []
            for filo in folder_files:
                file_list.append({'id': filo.id, 'name': filo.name, 'hash': filo.repo_hash, 'path': filo.data.path})
            updated_files = git_manager.update_files(file_list)
            # get list of updated files from git
            for filo in updated_files:
                Files.objects.filter(id=filo['id']).update(repo_status=filo['succeess'], repo_hash=filo['hash'])
                # Run celery parse delay task
                logger.info(f"File object updated ID: {filo['id']}. Sending parse task to celery.")
                file_manager = LocalizeFileManager(filo['id'])
                if file_manager.error or not file_manager.parse():
                    logger.warning(f'File parse error id:{filo['id']} err: {file_manager.error}')
                    file_manager.save_error()
        else:
            folder_files.update(repo_founded=None, repo_hash='')

