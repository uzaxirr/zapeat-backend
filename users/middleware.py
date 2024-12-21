from rest_framework.permissions import BasePermission

class IsRestaurantOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'RESTAURANT_OWNER'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'
