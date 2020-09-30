import logging

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from core.models import Folders, FolderRepo, Files
from core.services.file_manager import LocalizeFileManager

from core.git.git_manager import GitManager

logger = logging.getLogger('logfile')


class LocalizeFolderManager:
    """ Manage project folders with GIT (have subclasses) """
    # TODO: Make as FolderGitManager

    def __init__(self, folder_id):
        self.__id = folder_id
        self.__folder = None
        self.__git_manager = None
        try:
            self.__folder = Folders.objects.get(id=self.__id)
        except ObjectDoesNotExist:
            logger.warning(f'Folder not found id:{self.__id}')

    @property
    def __git(self):
        if not self.__git_manager:
            self.__git_manager = GitManager()
        return self.__git_manager

    def change_repo_access(self, access):
        if not self.__folder:
            logger.warning('Folder object not set')
            return False

    def change_repo_url(self, repo_url):    # TODO: Make 2 func - control and __incapsulated
        """ This func must be used when repo_url != folder.repo_url """
        if not self.__folder:
            logger.warning('Folder object not set')
            return False
        logger.info(f'Deleting old repo obj for folder id:{self.__id}')
        FolderRepo.objects.filter(folder_id=self.__id).delete()  # Mb exist or not
        folder_files = self.__folder.files_set.all()
        # Set folder repo status - updating  (if url empty - status don't checked in UI)
        logger.info(f'For folder id:{self.__id} changing repo status to: None - updating')
        self.__folder.repo_status = None
        self.__folder.save()
        logger.info(f'For files in folder id:{self.__id} changing repo status to: None and empty hash - no git control')
        folder_files.update(repo_status=None, repo_hash='')
        if not repo_url:    # Input URL empty
            return True
        # Check folder and files from new repo URL
        # git_manager = GitManage()
        self.__git.url = repo_url
        if not self.__git.sha:   # URL not exist or no access
            logger.warning(f'For folder id:{self.__id} changing folder repo status to: False - {self.__git.error}')
            self.__folder.repo_status = False
            self.__folder.save()
            return False
        if self.__git.error:
            logger.warning(f'Git manager error: {self.__git.error}')
            return False
        logger.info(f'For folder id:{self.__id} changing folder repo status to: True - checked')
        self.__folder.repo_status = True
        self.__folder.save()
        logger.info(f'Creating new repo obj for folder id:{self.__id}')
        defaults = {**self.__git.repo, 'hash': self.__git.sha}
        repo_obj, created = FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)

        self.__update_files_from_repo()

    def update_files(self):
        """ To run by celery scheduler to update files from repo folder """
        if not self.__folder:
            logger.warning('Folder object not set')
            return False
        if self.__folder.repo_status:
            # git_manager = GitManage()
            self.__git.repo = model_to_dict(self.__folder.folderrepo)
            if self.__git.check_repo:
                self.__update_files_from_repo()

    def __update_files_from_repo(self):
        if self.__git.need_update:  # Folder exist and new hash
            logger.info(f'For files in folder id:{self.__id} changing repo status to: False - 404')
            folder_files = self.__folder.files_set.all()
            folder_files.update(repo_status=False)
            # Creating list of files obj for git_manager checker
            file_list = []
            for filo in folder_files:
                file_list.append({'id': filo.id, 'name': filo.name, 'hash': filo.repo_hash, 'path': filo.data.path})
            # Get list of updated files from git
            updated_files = self.__git.update_files(file_list)
            logger.info(f'New files({len(updated_files)}) downloaded from repo for folder id:{self.__id}')
            for filo in updated_files:
                if not filo['updated']:
                    if filo['hash']:
                        logger.error(f"File id:{filo['id']} found in repository folder but failed to save on disk")
                    else:
                        logger.info(f"File id:{filo['id']} not found in repository folder")
                else:
                    logger.info(f"For file id:{filo['id']} changing status to: True - downloaded")
                    Files.objects.filter(id=filo['id']).update(repo_status=True, repo_hash=filo['hash'], state=1)
                    file_manager = LocalizeFileManager(filo['id'])
                    logger.info(f"File id:{filo['id']} start parse process")
                    if file_manager.error or not file_manager.parse():
                        logger.warning(f"File parse error id:{filo['id']} err: {file_manager.error} - retry once")
                        if not file_manager.parse():   # FIXME: create task to retry (task in task) ?
                            logger.warning(f"File parse second error id:{filo['id']} err: {file_manager.error}")
                            err_file_id, err_msg = file_manager.save_error()
                            logger.error(f'Created error file (id:{err_file_id}) saved: {err_msg}')
