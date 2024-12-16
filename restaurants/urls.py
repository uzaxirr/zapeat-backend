from django.urls import path
from .views import RestaurantListView, RestaurantDetailView, S3PreSignedUrlView

urlpatterns = [
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('images', S3PreSignedUrlView.as_view(), name='restaurant-images'),

]