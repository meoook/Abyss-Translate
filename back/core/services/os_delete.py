import logging
import os

from django.conf import settings

logger = logging.getLogger('django')


class DeleteInOS:
    """ Class with static methods to delete files or folders when corresponding model_name object deleted """

    @staticmethod
    def file_name_from_instance(instance, filename):
        """ Path for new File object - users/<user_id>/<prj_id>/<folder_id>/<file_name> """
        folder = instance.folder
        return '{}/{}/{}/{}'.format(folder.project.owner.id, folder.project.id, folder.id, instance.name)

    @staticmethod
    def delete_object(model_name: str, path_name: str) -> bool:
        """ Return True if model object deleted in OS """
        logger.info(f'OS delete object {model_name} with path {path_name}')
        if model_name == 'file':
            return DeleteInOS.__os_del_file(path_name)
        elif model_name == 'copy':
            return DeleteInOS.__os_del_file(path_name)
        elif model_name == 'folder':
            return DeleteInOS.__delete_folder(path_name)
        elif model_name == 'project':
            return DeleteInOS.__delete_folder(path_name)
        else:
            logger.error(f'Model {model_name} have no method to delete in OS')
            return False

    @staticmethod
    def __delete_folder(folder_path: str) -> bool:
        """ Delete folder, files and subfolders in OS """
        _root_path = os.path.join(settings.MEDIA_ROOT, folder_path)
        if os.path.isdir(_root_path):
            # Delete all files and sub folders
            for _root, _dirs, _files in os.walk(_root_path, topdown=False):
                for _file_name in _files:
                    _file_path = os.path.join(_root, _file_name)
                    DeleteInOS.__os_del_file(_file_path)
                for _folder_name in _dirs:
                    _folder_path = os.path.join(_root, _folder_name)
                    DeleteInOS.__os_del_folder(folder_path)
            # Delete root dir
            try:
                settings.STORAGE_ROOT.delete(folder_path)
            except ValueError:
                logger.error(f'OS delete root folder {_root_path} value fail')
            except OSError:
                logger.error(f'OS delete root folder {_root_path} os fail')
            else:
                logger.debug(f'OS delete root folder {_root_path} success')
                return True
        else:
            logger.error(f'OS not found directory {_root_path} to delete')
        return False

    @staticmethod
    def __os_del_file(_path: str) -> bool:
        logger.debug(f'OS called file {_path} to delete ')
        if os.path.isfile(_path):
            try:
                os.remove(_path)
            except OSError as _err:
                logger.error(f'OS delete file {_path} error:{_err}')
            else:
                logger.debug(f'OS delete file {_path} success')
                return True
        else:
            logger.error(f'OS not found file {_path} to delete')
        return False

    @staticmethod
    def __os_del_folder(_path: str) -> bool:
        logger.debug(f'OS called folder {_path} to delete')
        if os.path.isdir(_path):
            try:
                os.rmdir(_path)
            except OSError as _err:
                logger.error(f'OS delete folder {_path} error {_err}')
            else:
                logger.debug(f'OS delete folder {_path} success')
                return True
        else:
            logger.error(f'OS not found folder {_path} to delete')
        return False
