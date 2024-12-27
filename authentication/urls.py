from django.urls import path
from .views import (
    SendVerificationCodeView,
    CustomerVerificationView,
    RestaurantStaffVerificationView
)

urlpatterns = [
    path('send-verification/', SendVerificationCodeView.as_view(), name='send_verification'),
    path('customer/', CustomerVerificationView.as_view(), name='customer_verification'),
    path('restaurant-staff/', RestaurantStaffVerificationView.as_view(), name='staff_verification'),
]