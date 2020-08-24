from rest_framework import permissions, filters

from django.db.models import Max, Subquery, Q
from .models import ProjectPermissions


class IsFileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('core.creator'):
            return False
        if request.method in permissions.SAFE_METHODS:
            file_id = request.query_params.get('file_id')
        else:
            file_id = request.data.get('file_id')
        return request.user.projects_set.filter(folder__file_id=file_id).exists()


class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('core.creator'):
            return False
        if request.method in permissions.SAFE_METHODS:
            save_id = request.query_params.get('save_id')
        else:
            save_id = request.data.get('save_id')
        return request.user.projects_set.filter(save_id=save_id).exists()


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):                # GET, POST, PUT, DELETE
        if view.action == 'create':
            return request.user.has_perm('core.creator')
        return True

    def has_object_permission(self, request, view, obj):    # GET-ID, PUT, DELETE
        if request.method in permissions.SAFE_METHODS:    # GET', 'OPTIONS' and 'HEAD'
            return True
        return request.user.projects_set.filter(id=obj.id).exists()


# class IsFileTranslator(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.has_perm('localize.translator'):
#             return False
#         if request.method in permissions.SAFE_METHODS:
#             save_id = request.query_params.get('save_id')
#         else:
#             save_id = request.data.get('save_id')
#         return request.user.projects_set.filter(save_id=save_id).exists()

#     def has_object_permission(self, request, view, obj):
#         if request.user.
#         if request.method in permissions.SAFE_METHODS:    # GET', 'OPTIONS' and 'HEAD'
#             return True
#         return request.user.projects_set.filter(id=obj.id).exists()



# class CanManageOrTranslator(permissions.BasePermission):
    # def has_object_permission(self, request, view, obj):    # GET-ID, PUT, DELETE
#         if request.method in permissions.SAFE_METHODS:    # GET', 'OPTIONS' and 'HEAD'
#             return True
#         return obj.user == request.user


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.user == request.user


# class CanChangePermission(permissions.BasePermission):
#     """ Users who can change object """
#     def has_object_permission(self, request, view, obj):
#         pass


# class IsOwnerFilterBackend(filters.BaseFilterBackend):
#     """ Filter that only allows users to see their own objects. """
#     def filter_queryset(self, request, queryset, view):
#         return queryset.filter(owner=request.user)

# # PROJECT PERMS
# class ProjectFilterBackend(filters.BaseFilterBackend):
#     """ Filter projects that user allows to see """
#     def filter_queryset(self, request, queryset, view):
#         return queryset.filter(Q(project_permissions__permission__isnull=False), Q(owner=request.user))

# class ProjectCanEditOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         """ The instance-level has_object_permission method will only be called if the view-level has_permission checks have already passed """
#         return True

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if obj.owner == request.user:
#             return True
#         return ProjectPermissions.objects.filter(user=request.user, project=obj, permission=1).count() > 0
