from rest_framework import permissions, filters

from django.db.models import Max, Subquery, Q
from .models import ProjectPermissions


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """ ProjectViewSet permission """
    def has_permission(self, request, view):                # GET, POST, PUT, DELETE
        if view.action == 'create':
            return request.user.has_perm('core.creator')
        return True

    def has_object_permission(self, request, view, obj):    # GET-ID, PUT, DELETE
        return request.user.projects_set.filter(id=obj.id).exists()


class IsProjectOwnerOrAdmin(permissions.BasePermission):
    """ Project manage access - owner and admin """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            save_id = request.query_params.get('save_id')
        else:
            save_id = request.data.get('save_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(save_id=save_id).exists()
        return request.user.projectpermissions_set.filter(project__save_id=save_id, permission=9).exists()


class IsProjectOwnerOrManage(permissions.BasePermission):
    """ Project manage rights to create folders - owner and manager """
    def has_permission(self, request, view):
        if request.method in (*permissions.SAFE_METHODS, 'POST'):
            save_id = request.query_params.get('save_id') or request.data.get('save_id')
            if request.user.has_perm('core.creator'):
                return request.user.projects_set.filter(save_id=save_id).exists()
            return request.user.projectpermissions_set.filter(project__save_id=save_id, permission=8).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folders__id=obj.id).exists()
        return request.user.projectpermissions_set.filter(project__folders__id=obj.id, permission=8).exists()


class IsFileOwnerOrHaveAccess(permissions.BasePermission):
    """ File manage rights - owner and manager or translator can list project files """
    def has_permission(self, request, view):
        if view.action == 'list':
            folder_id = request.query_params.get('folder_id')
            if request.user.has_perm('core.creator'):
                return request.user.projects_set.filter(folders__id=folder_id).exists()
            if folder_id:
                return request.user.projectpermissions_set.filter(project__folders__id=folder_id, permission=8).exists()
            save_id = request.query_params.get('save_id')
            return request.user.projectpermissions_set.filter(project__save_id=save_id, permission=0).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folders__files__id=obj.id).exists()
        return request.user.projectpermissions_set.filter(project__folders__files__id=obj.id, permission=8).exists()


class IsFileOwnerOrTranslator(permissions.BasePermission):
    """ File translate rights - owner and manager """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            file_id = request.query_params.get('file_id')
        else:
            file_id = request.data.get('file_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folders__file__id=file_id).exists()
        return request.user.projectpermissions_set.filter(project__folders__file__id=file_id, permission=0).exists()


class IsFileOwnerOrManager(permissions.BasePermission):
    """ File transfer rights - owner and manager """
    def has_permission(self, request, view):    # Post files
        if request.method in permissions.SAFE_METHODS:
            return True
        folder_id = request.data.get('folder_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folders__id=folder_id).exists()
        return request.user.projectpermissions_set.filter(project__folder_id=folder_id, permission=8).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.has_perm('core.creator'):
                return request.user.projects_set.filter(folder__file_id=obj.id).exists()
            return request.user.projectpermissions_set.filter(project__folder__file_id=obj.id, permission=8).exists()
        return False


def get_user_perms(user, obj_id, obj_class):
    """
    Experimental function - better not to use
    Return owner status for creator or permissions array (no perms will return empty array)
    """
    owner = False
    if user.has_perm('core.creator'):
        if obj_class == 'file':
            owner = user.projects_set.filter(project__folder__file_id=obj_id).count() > 0
        elif obj_class == 'folder':
            owner = user.projects_set.filter(project__folder_id=obj_id).count() > 0
        elif obj_class == 'project':
            owner = user.projects_set.filter(project_save_id=obj_id).count() > 0
    elif obj_class == 'file':
        return user.projectpermissions_set.filter(project__folder__file_id=obj_id)
    elif obj_class == 'folder':
        return user.projectpermissions_set.filter(project__folder_id=obj_id)
    elif obj_class == 'project':
        return user.projectpermissions_set.filter(project_save_id=obj_id)
    return [x for x in range(20)] if owner else []
