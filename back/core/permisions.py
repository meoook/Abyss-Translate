from rest_framework import permissions, filters

from django.db.models import Max, Subquery, Q
from .models import ProjectPermissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class CanChangePermission(permissions.BasePermission):
    """ Users who can change object """
    def has_object_permission(self, request, view, obj):
        pass


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """ Filter that only allows users to see their own objects. """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)

# PROJECT PERMS
class ProjectFilterBackend(filters.BaseFilterBackend):
    """ Filter projects that user allows to see """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(Q(project_permissions__permission__isnull=False), Q(owner=request.user))

class ProjectCanEditOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        """ The instance-level has_object_permission method will only be called if the view-level has_permission checks have already passed """
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.owner == request.user:
            return True
        return ProjectPermissions.objects.filter(user=request.user, project=obj, permission=1).count() > 0