from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerOrBusinessUserOrAdmin(BasePermission):
    """
    Custom permission to allow access for customer, business user, or admin.
    - `POST`: Only customers can create orders.
    - `GET`, `PATCH`, `PUT`: Accessible by the customer or business user associated with the order, or admin users.
    - `DELETE`: Only accessible by admin users.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.type == 'customer'
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user == obj.business_user or request.user == obj.customer_user or request.user.is_superuser
        if request.method in ["PATCH", "PUT"]:
            return request.user == obj.business_user or request.user.is_superuser
        if request.method == "DELETE":
            return request.user.is_superuser
        return True
