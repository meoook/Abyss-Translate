from rest_framework import permissions, filters


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """ Filter that only allows users to see their own objects. """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)
