from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Custom permission class that grants read-only access to any request
    but allows write operations only if the requesting user is authenticated and the object's owner oder admin user.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and (request.user == obj.user or request.user.is_superuser))