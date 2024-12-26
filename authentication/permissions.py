from rest_framework import permissions

from authentication.models import RestaurantStaff


class IsRestaurantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        restaurant_id = view.kwargs.get('restaurant_pk')
        return RestaurantStaff.objects.filter(
            user=request.user,
            restaurant_id=restaurant_id,
            role='RESTAURANT_ADMIN',
            is_active=True
        ).exists()

class HasRestaurantStaffRole(permissions.BasePermission):
    def has_permission(self, request, view):
        restaurant_id = view.kwargs.get('restaurant_pk')
        return RestaurantStaff.objects.filter(
            user=request.user,
            restaurant_id=restaurant_id,
            is_active=True
        ).exists()