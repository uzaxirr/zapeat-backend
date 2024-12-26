from rest_framework import permissions

class IsRestaurantStaffMember(permissions.BasePermission):
    def has_permission(self, request, view):
        restaurant_id = view.kwargs.get('restaurant_id')
        return request.user.staff_roles.filter(
            restaurant_id=restaurant_id,
            is_active=True
        ).exists()
    