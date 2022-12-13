from rest_framework.permissions import BasePermission


class IsOwnDataOrSuperuser(BasePermission):
    """
    Validates if the data is from the current user or
    user is superuser
    """

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user.id or request.user.is_superuser


class IsOwnData(BasePermission):
    """
    Validates if the data is from the current user
    """

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id
