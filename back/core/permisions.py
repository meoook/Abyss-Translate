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
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            save_id = request.query_params.get('save_id')
        else:
            save_id = request.data.get('save_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(save_id=save_id).exists()
        return request.user.projectpermissions_set.filter(project__save_id=save_id, permission=9).exists()


class IsProjectOwnerOrManage(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            save_id = request.query_params.get('save_id')
        else:
            save_id = request.data.get('save_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(save_id=save_id).exists()
        return request.user.projectpermissions_set.filter(project__save_id=save_id, permission=8).exists()


class IsFileOwnerOrHaveAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list':
            folder_id = request.query_params.get('folder_id')
            if request.user.has_perm('core.creator'):
                return request.user.projects_set.filter(folder_id=folder_id).exists()
            if folder_id:
                return request.user.projectpermissions_set.filter(project__folder_id=folder_id, permission=8).exists()
            save_id = request.query_params.get('save_id')
            return request.user.projectpermissions_set.filter(project_save_id=save_id, permission=0).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folder__file_id=obj.id).exists()
        return request.user.projectpermissions_set.filter(project__folder__file_id=obj.id, permission=8).exists()


class IsFileOwnerOrTranslator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            file_id = request.query_params.get('file_id')
        else:
            file_id = request.data.get('file_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folder__file_id=file_id).exists()
        return request.user.projectpermissions_set.filter(project__folder__file_id=file_id, permission=0).exists()


class IsFileOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        folder_id = request.data.get('folder_id')
        if request.user.has_perm('core.creator'):
            return request.user.projects_set.filter(folder_id=folder_id).exists()
        return request.user.projectpermissions_set.filter(project__folder_id=folder_id, permission=0).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.has_perm('core.creator'):
                return request.user.projects_set.filter(folder__file_id=obj.id).exists()
            return request.user.projectpermissions_set.filter(project__folder__file_id=obj.id, permission=0).exists()
