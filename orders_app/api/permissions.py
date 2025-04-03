from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerOrAdminOrReadOnly(BasePermission):
    """
    Custom permission class that grants read-only access to any request
    but allows write operations only if the requesting user is the object's owner.
    """
    def has_object_permission(self, request, view, obj):
        """
        Returns True if the request method is safe (read-only).
        Otherwise, grants permission only if the requesting user is the object's owner.
        """
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and (request.user == obj.user or request.user.is_superuser) and (request.user.type == "customer"))