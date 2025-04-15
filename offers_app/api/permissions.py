from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Custom permission class that grants read-only access to any request
    but allows write operations only if the requesting user is authenticated and the object's owner or admin user.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            if view.action == 'list':
                return True
            if view.action == 'retrieve' and not request.user.is_authenticated:
                return False
            return True
        if request.method == 'POST':
            return bool(
                request.user.is_authenticated and (request.user.type == 'business' or request.user.is_superuser))
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and ((request.user == obj.user and request.user.type == "business") or request.user.is_superuser))