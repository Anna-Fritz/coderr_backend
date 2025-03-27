from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission class that grants access to the object if the user is the owner of the object or an admin (superuser).

    For DELETE requests, only admins (superusers) are allowed.
    For other requests, the user must either be the owner of the object or an admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        return bool(request.user and (request.user == obj.user or request.user.is_superuser))
