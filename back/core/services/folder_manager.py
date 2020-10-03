import logging

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from core.git.git_oauth2 import GitOAuth2
from core.models import Folders, FolderRepo, Files
from core.services.file_manager import LocalizeFileManager

from core.git.git_manager import GitManager

logger = logging.getLogger('logfile')


class LocalizeFolderManager:
    """ Manage project folders with GIT (have subclasses) """

    # TODO: Make as FolderGitManager

    def __init__(self, folder_id):
        self.__id = folder_id
        self.__git = GitManager()
        try:
            self.__folder = Folders.objects.get(id=self.__id)
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
        if access_type not in ['basic', 'token', 'bearer', 'oauth']:  # Support access types
            logger.warning(f'Unknown access type:{access_type}')
            error_for_user = 'Access type error'
        else:
            if access_type == 'oauth':
                oauth = GitOAuth2(repo_obj.provider)
                access_value, err = oauth.refresh_token(access_value)  # Get refresh token by code
                if err:
                    logger.warning(f'For folder id:{repo_obj.folder_id} OAuth get access error for provider:{repo_obj.provider}')
                    error_for_user = 'OAuth access error'
        if error_for_user:
            repo_obj.error = error_for_user
            repo_obj.save()
        else:
            repo_obj.access = {'type': access_type, 'token': access_value}
            repo_obj.save()
            try:
                self.__git.repo = model_to_dict(repo_obj)
                new_sha = self.__git.sha
            except AssertionError as err:
                logger.warning(f'Setting repository for folder id:{self.__id} error {err}')
                repo_obj.error = 'Access to repository error'
                self.__folder.repo_status = False
            else:
                repo_obj.sha = new_sha
                self.__folder.repo_status = True
            repo_obj.save()
            self.__folder.folderrepo.save()

    def __check_repo_access(self, access_type, access_value):
        pass

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
        if not self.__url:  # Input URL empty
            return True
        self.__repo_url_check()  # Input URL not empty

    def __repo_url_check(self):
        """ If URL not empty - check repository """
        repo_status = False
        try:  # Input URL not empty
            self.__git.url = self.__url  # Create repository object from URL
            if self.__git.sha:  # Repository found
                repo_status = True
            else:  # URL not found or no access
                logger.warning(f'For folder id:{self.__id} changing folder repo status to: False - not found')
        except AssertionError as err:
            logger.warning(f'Git error: {err} - changed folder id:{self.__id} repo status to: False - not found')
        else:
            logger.info(f'For folder id:{self.__id} changing folder repo status to: True - found')
        self.__folder.repo_status = repo_status
        self.__folder.save()
        if self.__git.repo:
            logger.info(f'Creating new repo obj for folder id:{self.__id}')
            defaults = {**self.__git.repo, 'sha': self.__git.sha if repo_status else ''}
            FolderRepo.objects.update_or_create(folder_id=self.__id, defaults=defaults)
        else:
            logger.warning(f"Can't create repo obj from url {self.__url}")

    def update_files(self):
        """ To run by celery to update files from repo folder """
        if self.__check_folder(__name__):
            folder_files = self.__folder.files_set.all()
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
                    Files.objects.filter(id=filo['id']).update(repo_status=True, repo_sha=new_file_sha, state=1)
                    file_manager = LocalizeFileManager(filo['id'])
                    logger.info(f"File id:{filo['id']} start parse process")
                    if file_manager.error or not file_manager.parse():
                        logger.warning(f"File parse error id:{filo['id']} err: {file_manager.error} - retry once")
                        if not file_manager.parse():  # FIXME: create task to retry (task in task) ?
                            error_files_amount += 1
                            logger.warning(f"File parse second error id:{filo['id']} err: {file_manager.error}")
                            err_file_id, err_msg = file_manager.save_error()
                            logger.error(f'Created error file (id:{err_file_id}) saved: {err_msg}')
                        else:
                            updated_files_amount += 1
                    else:
                        updated_files_amount += 1
                    file_manager.update_all_language_progress()
        return updated_files_amount, error_files_amount

    def __check_folder(self, method):
        """ Your program is incorrect if this error appear """
        if not self.__folder:
            logger.error(f'Folder object not set when run method {method}')
            return False
        return True
