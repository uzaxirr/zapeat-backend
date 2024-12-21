from django.urls import path
from .views import (
    RestaurantListView,
    RestaurantDetailView,
    S3PreSignedUrlView, RestaurantMenuAPIView,
    MenuCategoryAPIView, MenuCategoryDetailAPIView,
    MenuItemAPIView, MenuItemDetailAPIView,
    CustomizationGroupAPIView, CustomizationGroupDetailAPIView,
    CustomizationOptionAPIView, CustomizationOptionDetailAPIView
)

urlpatterns = [
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/menu/', RestaurantMenuAPIView.as_view(), name='restaurant-menu'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('images', S3PreSignedUrlView.as_view(), name='restaurant-images'),

    # Menu Category URLs
    path('categories/', MenuCategoryAPIView.as_view(), name='category-list'),
    path('categories/<int:pk>/', MenuCategoryDetailAPIView.as_view(), name='category-detail'),

    # Menu Item URLs
    path('items/', MenuItemAPIView.as_view(), name='menuitem-list'),
    path('items/<int:pk>/', MenuItemDetailAPIView.as_view(), name='menuitem-detail'),

    # Customization Group URLs
    path('groups/', CustomizationGroupAPIView.as_view(), name='group-list'),
    path('groups/<int:pk>/', CustomizationGroupDetailAPIView.as_view(), name='group-detail'),

    # Customization Option URLs
    path('options/', CustomizationOptionAPIView.as_view(), name='option-list'),
    path('options/<int:pk>/', CustomizationOptionDetailAPIView.as_view(), name='option-detail'),
]