import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from core.models import File, Translated, Folder, Project

logger = logging.getLogger('django')


def on_create_file_path(instance, filename):
    """ Path for new File object - users/<user_id>/<prj_id>/<folder_id>/<file_id> """
    folder = instance.folder
    return '{}/{}/{}/{}'.format(folder.project.owner.id, folder.project.id, folder.id, instance.name)


def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes file from filesystem when corresponding `File` or `Translated` object is deleted. """
    if instance.translate_copy:
        _instance_data = instance.translate_copy.path
        try:
            if os.path.isfile(_instance_data.path):
                print('Delete file -> onDelete File object', _instance_data.path)
                _instance_data.delete(save=False)
        except ValueError:
            print("Trigger auto_delete_file_on_delete - system error")
    else:
        print("Error: trigger auto_delete_file_on_delete - input wrong instance")
    return


class DeleteInOS:
    """ Class to delete files or folders when corresponding model_name object deleted """
    @staticmethod
    def delete_object(model_name: str, obj_id: int) -> bool:
        """ Return True if model object deleted in OS """
        if model_name == 'file':
            return DeleteInOS.__delete_file(obj_id)
        elif model_name == 'copy':
            return DeleteInOS.__delete_file(obj_id)
        elif model_name == 'folder':
            return DeleteInOS.__delete_folder(obj_id)
        elif model_name == 'project':
            return DeleteInOS.__delete_folder(obj_id)
        else:
            logger.error(f'Model:{model_name} have no method to delete in OS')
            return False

    @staticmethod
    def __delete_file(obj_id: int) -> bool:
        _model = File.objects
        _instance = DeleteInOS.__get_instance(_model, obj_id)
        if _instance:
            return DeleteInOS.__os_del_file('file', _instance.data)
        return False

    @staticmethod
    def __delete_translated(obj_id: int) -> bool:
        _model = Translated.objects
        _instance = DeleteInOS.__get_instance(_model, obj_id)
        if _instance:
            return DeleteInOS.__os_del_file('copy', _instance.translate_copy)
        return False

    @staticmethod
    def __delete_folder(obj_id: int) -> bool:
        _model = Folder.objects
        _instance = DeleteInOS.__get_instance(_model, obj_id)
        if _instance:
            _folder_path = '{}/{}/{}/'.format(_instance.project.owner.id, _instance.project.id, _instance.id)
            return DeleteInOS.__os_del_folder('folder', _folder_path)
        return False

    @staticmethod
    def __delete_project(obj_id: int) -> bool:
        _model = Project.objects
        _instance = DeleteInOS.__get_instance(_model, obj_id)
        if _instance:
            _folder_path = '{}/{}/'.format(_instance.owner.id, _instance.id)
            return DeleteInOS.__os_del_folder('project', _folder_path)
        return False

    @staticmethod
    def __os_del_file(model_name: str, instance_data) -> bool:
        _path: str = instance_data.path
        if os.path.isfile(_path):
            logger.info(f'OS try to delete {model_name} path:{_path}')
            try:
                instance_data.delete(save=False)
            except ValueError:
                logger.error(f'OS delete {model_name} path:{_path} - fail')
            else:
                logger.info(f'OS delete {model_name} path:{_path} - success')
                return True
        else:
            logger.error(f'OS not found file path:{_path} to delete')
        return False

    @staticmethod
    def __os_del_folder(model_name: str, folder_path: str) -> bool:
        _path = os.path.join(settings.MEDIA_ROOT, folder_path)
        if os.path.isdir(_path):
            try:
                settings.STORAGE_ROOT.delete(folder_path, save=False)
            except ValueError:
                logger.error(f'OS delete {model_name} path:{_path} - value fail')
            except OSError:
                logger.error(f'OS delete {model_name} path:{_path} - os fail')
            else:
                logger.info(f'OS delete {model_name} path:{_path} - success')
                return True
        else:
            logger.error(f'OS not found directory path:{_path} to delete or not a dir')
        return False

    @staticmethod
    def __get_instance(model, obj_id: int):
        try:
            return model.get(pk=obj_id)
        except ObjectDoesNotExist:
            logger.error(f'Object with id:{obj_id} not found in model')
