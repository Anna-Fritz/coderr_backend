from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        return bool(request.user and (request.user == obj.user or request.user.is_superuser))
