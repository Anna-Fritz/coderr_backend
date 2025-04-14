from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerOrBusinessUserOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user and request.user.type == 'customer'
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user == obj.business_user or request.user == obj.customer_user or request.user.is_superuser
        if request.method in ["PATCH", "PUT"]:
            business_user = getattr(obj.business_user, "user", obj.business_user)
            return request.user == business_user or request.user.is_superuser
        if request.method == "DELETE":
            return request.user and request.user.is_superuser
        return True
