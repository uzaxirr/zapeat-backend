from django.urls import path
from .views import (
    RestaurantOrderView
)

# urlpatterns = [
#     path('', OrderListCreateAPIView.as_view(), name='order-detail'),
#     path('order/', RestaurantOrdersView.as_view(), name='order-list-create'),
#     path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
#     path('order-items/', OrderItemListCreateAPIView.as_view(), name='order-item-list-create'),
#     path('order-items/<int:pk>/', OrderItemDetailAPIView.as_view(), name='order-item-detail'),
# ]

urlpatterns = [
    path('', RestaurantOrderView.as_view(), name='order-detail'),
    # path('order/', RestaurantOrdersView.as_view(), name='order-list-create'),
    # path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    # path('order-items/', OrderItemListCreateAPIView.as_view(), name='order-item-list-create'),
    # path('order-items/<int:pk>/', OrderItemDetailAPIView.as_view(), name='order-item-detail'),
]
