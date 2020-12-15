import os

from django.conf import settings


def on_create_file_path(instance, filename):
    """ Path for new File object - users/<user_id>/<prj_id>/<folder_id>/<file_id> """
    folder = instance.folder
    return '{}/{}/{}/{}'.format(folder.project.owner.id, folder.project.id, folder.id, instance.name)


def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes file from filesystem when corresponding `File` or `Translated` object is deleted. """
    if sender._meta.model_name == 'file':
        inst_obj = instance.data
    elif sender._meta.model_name == 'translated':
        if instance.translate_copy:
            inst_obj = instance.translate_copy
        else:
            return
    else:
        print("Error: trigger auto_delete_file_on_delete - input wrong instance")
        return
    try:
        if os.path.isfile(inst_obj.path):
            print('Delete file -> onDelete File object', inst_obj.path)
            # os.remove(instance.file.path)
            inst_obj.delete(save=False)
    except ValueError:
        pass


# TODO: for prj and folder -> one function
def auto_delete_folder_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Folder` object is deleted. """
    path_to_delete = '{}/{}/{}/'.format(instance.project.owner.username, instance.project.id, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete folder -> onDelete Folder object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)


def auto_delete_project_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Project` object is deleted. """
    path_to_delete = '{}/{}/'.format(instance.owner.username, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete project folder -> onDelete Project object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)
