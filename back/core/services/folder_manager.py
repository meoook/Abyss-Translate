import logging

from django.core.exceptions import ObjectDoesNotExist

from core.models import Folders, FolderRepo, Files
from core.services.file_manager import LocalizeFileManager

from core.services.git_manager import GitManage

logger = logging.getLogger('django')


class LocalizeFolderManager:
    """ Manage project folders (have subclasses) """

    def __init__(self, folder_id):
        self.__id = folder_id
        self.__folder = None
        try:
            self.__folder = Folders.objects.get(id=self.__id)
        except ObjectDoesNotExist:
            logger.warning(f'Folder not found id:{self.__id}')

    def change_repo_url(self, repo_url):
        """ This func must be used when repo_url != folder.repo_url """
        if not self.__folder:
            logger.warning('Folder object not set')
            return False
        logger.info(f'Deleting old repo obj for folder id:{self.__id}')
        FolderRepo.objects.filter(folder_id=self.__id).delete()  # Mb exist or not
        folder_files = self.__folder.files_set.all()
        # Set folder repo status - updating  (if url empty - status don't checked in UI)
        logger.info(f'Changing folder repo status to: updating(None) for folder id:{self.__id}')
        self.__folder.save(repo_status=None)
        logger.info(f'Changing repo status to: empty url or error(None) for files in folder id:{self.__id}')
        folder_files.update(repo_status=None, repo_hash='')
        if not repo_url:    # Input URL empty
            return True
        # Check folder and files from new repo URL
        git_manager = GitManage()
        if not git_manager.check_url(repo_url):   # URL not exist or no access
            logger.warning(f'Changing folder repo status to: error(False) for folder id:{self.__id}')
            self.__folder.save(repo_status=False)
            return False
        if git_manager.error:
            logger.warning(f'Git manager error: {git_manager.error}')
            return False
        logger.info(f'Changing folder repo status to: checked(True) for folder id:{self.__id}')
        self.__folder.save(repo_status=None)
        logger.info(f'Creating new repo obj for folder id:{self.__id}')
        defaults = {**git_manager.repo, 'hash': git_manager.new_hash}
        repo_obj, created = FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)

        self.__update_files_from_repo(git_manager)

    def update_files(self):
        """ To run by celery scheduler to update files from repo folder """
        if not self.__folder:
            logger.warning('Folder object not set')
            return False
        if self.__folder.repo_status:
            git_manager = GitManage()
            git_manager.repo = self.__folder.folderrepo
            if git_manager.check_repo:
                self.__update_files_from_repo(git_manager)

    def __update_files_from_repo(self, git_manager):
        if git_manager.need_update:  # Folder exist and new hash
            logger.info(f'Changing repo status to: 404(False) for files in folder id:{self.__id}')
            folder_files = self.__folder.files_set.all()
            folder_files.update(repo_status=False)
            # Creating list of files obj for git_manager checker
            file_list = []
            for filo in folder_files:
                file_list.append({'id': filo.id, 'name': filo.name, 'hash': filo.repo_hash, 'path': filo.data.path})
            # Get list of updated files from git
            updated_files = git_manager.update_files(file_list)
            logger.info(f'New files({len(updated_files)}) downloaded from repo for folder id:{self.__id}')
            for filo in updated_files:
                logger.info(f"For file id:{filo['id']} changing status to downloaded and start parse process")
                Files.objects.filter(id=filo['id']).update(repo_status=filo['success'], repo_hash=filo['hash'], state=1)
                file_manager = LocalizeFileManager(filo['id'])
                if file_manager.error or not file_manager.parse():
                    logger.warning(f"File parse error id:{filo['id']} err: {file_manager.error} - retry")
                    if not file_manager.parse():   # FIXME: create task to retry (task in task) ?
                        logger.warning(f"File parse error id:{filo['id']} err: {file_manager.error}")
                        err_file_id, err_msg = file_manager.save_error()
                        logger.error(f'Created error file (id:{err_file_id}) saved: {err_msg}')
