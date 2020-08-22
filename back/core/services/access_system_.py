from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


def project_check_perm_or_404(save_id, user, perm):
    try:
        if user.has_perm('localize.creator'):
            user.project_set.get(save_id=save_id)
        else:
            user.project_permisions_set.get(permission=perm, project_save_id=save_id)
    except ObjectDoesNotExist:
        raise Http404
    return True


def folder_check_perm_or_404(folder_id, user, perm):
    try:
        if user.has_perm('localize.creator'):
            user.project_set.get(folder_id=folder_id)
        else:
            user.project_permisions_set.get(permission=perm, project__folder_id=folder_id)
    except ObjectDoesNotExist:
        raise Http404
    return True


def file_check_perm_or_404(file_id, user, perm):
    try:
        if user.has_perm('localize.creator'):
            user.project_set.get(folder__file_id=file_id)
        else:
            user.project_permisions_set.get(permission=perm, project__folder__file_id=file_id)
    except ObjectDoesNotExist:
        raise Http404
    return True


def get_user_perms(user, obj_id, obj_class):
    """ Return owner status for creator or permissions array (no perms will return empty array) """
    owner = False
    if user.has_perm('localize.creator'):
        if obj_class == 'file':
            owner = user.project_set.filter(project__folder__file_id=obj_id).count() > 0
        elif obj_class == 'folder':
            owner = user.project_set.filter(project__folder_id=obj_id).count() > 0
        elif obj_class == 'project':
            owner = user.project_set.filter(project_save_id=obj_id).count() > 0
    elif obj_class == 'file':
        return user.project_permisions_set.filter(project__folder__file_id=obj_id)
    elif obj_class == 'folder':
        return user.project_permisions_set.filter(project__folder_id=obj_id)
    elif obj_class == 'project':
        return user.project_permisions_set.filter(project_save_id=obj_id)
    return [x for x in range(20)] if owner else []
