from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserTypeOrAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return request.user and request.user.is_authenticated and request.user.type == 'customer'
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method in ["PATCH", "PUT"]:
            business_user = getattr(obj.business_user, "user", obj.business_user)
            return request.user == business_user or request.user.is_superuser
        if request.method == "DELETE":
            return request.user.is_superuser
        return False
