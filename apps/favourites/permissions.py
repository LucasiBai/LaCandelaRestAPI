from rest_framework.permissions import BasePermission


class IsOwnFavItemOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Validates if request user is owner of current obj
        """
        return (obj.user.id == request.user.id) or request.user.is_superuser
