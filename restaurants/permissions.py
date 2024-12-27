from rest_framework import permissions

class IsRestaurantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        restaurant_id = view.kwargs.get('pk')  # Get restaurant ID from URL
        return request.user.is_restaurant_admin(restaurant_id)
    