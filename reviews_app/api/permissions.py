from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReviewerOrBusinessUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated and request.user.type == "customer"
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.reviewer or request.user == obj.business_user
        if request.method in ["PATCH", "PUT"]:
            return request.user == obj.reviewer
        if request.method == "DELETE":
            return request.user == obj.reviewer or request.user.is_superuser
        return False
