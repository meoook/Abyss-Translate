import logging

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from core.services.file_interface.file_interface import FileInterface
from core.services.git_interface.git_auth import OAuth2Token

from core.models import Folder, FolderRepo, File
# from core.services.tmp_file_system.file_interface import LocalizeFileInterface

from core.services.git_interface.git_interface import GitInterface

logger = logging.getLogger('logfile')


class LocalizeGitFolderInterface:
    """ Manage project folders with GIT (have subclasses) """

    def __init__(self, folder_id):
        self.__id = folder_id
        self.__git = GitInterface()
        try:
            self.__folder = Folder.objects.get(id=self.__id)
            self.__url = self.__folder.repo_url
        except ObjectDoesNotExist:
            logger.warning(f'Folder not found id:{self.__id}')

    def change_repo_access(self, access_type, access_value):
        """ Check repository access and exist status with new credentials (update model object) """
        if not self.__check_folder(__name__):
            return False
        logger.info(f'Repository check access for folder id:{self.__id}')
        error_for_user = None
        repo_obj = self.__folder.folderrepo
        # Income data check
        if access_type not in ['ssh', 'token', 'oauth', 'abyss']:  # Support access types
            logger.warning(f'Unknown access type:{access_type}')
            error_for_user = 'Access type error'
        else:
            if access_type == 'oauth':
                access_value = OAuth2Token(repo_obj.provider, access_value)  # Get refresh token by code
                if not access_value:
                    logger.warning(f'For folder id:{repo_obj.folder_id} OAuth get access error')
                    error_for_user = 'OAuth access error'
        # Update folder and repo objects
        if error_for_user:
            repo_obj.error = error_for_user
            repo_obj.save()
        else:  # No problems from user side (access e.t.c.)
            repo_obj.access = {'type': access_type, 'token': access_value}
            repo_obj.save()  # need repo_obj with access on next step
            if self.__folder_update_git_status(repo_obj, 'obj'):
                repo_obj.sha = self.__git.sha
            else:
                logger.warning(f'Setting repository for folder id:{self.__id} error ')
                repo_obj.error = 'Access error'
            repo_obj.save()

    def repo_url_changed(self):
        """ Check repository access and exist status """
        if not self.__check_folder(__name__):
            return False
        logger.info(f'Deleting old repo obj for folder id:{self.__id}')
        FolderRepo.objects.filter(folder_id=self.__id).delete()  # Mb exist or not
        # Set folder repo status - updating  (if url empty - status don't checked in UI)
        logger.info(f'For folder id:{self.__id} changing repo status to: None - updating')
        self.__folder.repo_status = None
        self.__folder.save()
        if self.__url:  # Input URL not empty
            self.__repo_url_check()

    def __repo_url_check(self):
        """ If URL not empty - check repository """
        sha = self.__git.sha if self.__folder_update_git_status(self.__url, 'url') else ''
        if self.__git.repo:
            logger.info(f'Creating new repo obj for folder id:{self.__id}')
            defaults = {**self.__git.repo, 'sha': sha}
            FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)
        else:
            logger.warning(f"Can't create repo obj from url {self.__url}")

    def __folder_update_git_status(self, value, value_type='obj'):
        """ Update repository model object status """
        repo_status = False
        try:
            # Create repository object
            if value_type == 'url':
                self.__git.url = value  # from URL
            else:
                self.__git.repo = model_to_dict(value)  # from repo model object
            # Check repository
            if self.__git.sha:  # Repository found
                repo_status = True
            else:  # URL not found or no access
                logger.warning(f'For folder id:{self.__id} changing folder repo status to: False - not found')
        except AssertionError as err:
            logger.warning(f'Git error: {err} - changed folder id:{self.__id} repo status to: False - not found')
        else:
            logger.info(f'For folder id:{self.__id} changing folder repo status to: True - found')
        # Update status
        self.__folder.repo_status = repo_status
        self.__folder.save()
        return repo_status

    def update_files(self):
        """ To run by celery to update files from repo folder """
        if self.__check_folder(__name__):
            folder_files = self.__folder.file_set.all()
            if not self.__url:
                logger.info(f'For files in folder id:{self.__id} changing repo status to: None - no git control')
                folder_files.update(repo_status=None, repo_sha='')  # TODO: really null hash ?
            else:
                logger.info(f'For files in folder id:{self.__id} changing repo status to: False - 404')
                folder_files.update(repo_status=False)
                try:
                    if not self.__git.repo or self.__folder.repo_status:  # If repository not set but status is ok
                        self.__git.repo = model_to_dict(self.__folder.folderrepo)
                    if self.__git.need_update:
                        f_amount = len(folder_files)  # FIXME : .count()
                        logger.info(f'Folder id:{self.__id} running update files from repository - amount {f_amount}')
                        updated_amount, error_amount = self.__update_files_from_repo(folder_files)
                        logger.info(f'New files({updated_amount}) downloaded from repository for folder id:{self.__id}')
                        if error_amount:
                            logger.warning(f'Error files({error_amount}) for folder id:{self.__id}')
                except AssertionError as err:
                    logger.error(err)

    def __update_files_from_repo(self, folder_files):
        # TODO: Add save warnings if repo fail update
        updated_files_amount = 0
        error_files_amount = 0
        if self.__git.need_update:  # Folder exist and new hash
            # Creating list of files obj for git_manager checker
            for filo in folder_files:
                try:
                    new_file_sha, err = self.__git.update_file(filo.data.path, filo.repo_hash)
                except AssertionError as error:
                    err = error
                    new_file_sha = None  # No need but without - IDE error
                if err:
                    error_files_amount += 1
                    logger.info(f"Error update file id:{filo['id']} from repository {err}")
                else:
                    logger.info(f"For file id:{filo['id']} changing status to: True - downloaded")
                    File.objects.filter(id=filo['id']).update(repo_status=True, repo_sha=new_file_sha)
                    file_manager = FileInterface(filo['id'])
                    logger.info(f"File id:{filo['id']} start parse process")
                    file_manager.file_refresh_original()
                    updated_files_amount += 1
        return updated_files_amount, error_files_amount

    def __check_folder(self, method):
        """ Your program is incorrect if this error appear """
        if not self.__folder:
            logger.error(f'Folder object not set when run method {method}')
            return False
        return True
