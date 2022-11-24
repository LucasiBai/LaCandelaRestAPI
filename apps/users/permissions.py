from rest_framework.permissions import BasePermission


class IsOwnData(BasePermission):
    """
    Validates if the data is from the current user
    """

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id
