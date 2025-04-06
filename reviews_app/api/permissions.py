from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReviewerOrBusinessUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.method == 'GET':
                return request.user == obj.reviewer or request.user == obj.business_user
            return True
        if request.method in ["POST", "PATCH", "PUT"]:
            return request.user == obj.reviewer
        if request.method == "DELETE":
            return request.user == obj.reviewer or request.user.is_superuser
        return False
