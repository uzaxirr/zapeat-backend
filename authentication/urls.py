from attr.filters import include
from django.urls import path
from .views import SendVerificationCodeView, VerifyPhoneView

urlpatterns = [
    path('send-verification/', SendVerificationCodeView.as_view(), name='send_verification'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify_phone'),
]
