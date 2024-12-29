import logging
from datetime import datetime, timedelta

import jwt
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from authentication.models import RestaurantStaff
from authentication.serializers import CustomerVerificationSerializer, PhoneVerifySerializer, PhoneSendVerificationSerializer, RestaurantStaffSerializer, RestaurantStaffVerificationSerializer
from zapeat import settings

from zapeat.std_utils import CustomAPIModule

class SendVerificationCodeView(APIView, CustomAPIModule):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PhoneSendVerificationSerializer,
        responses={
            200: openapi.Response('Verification code sent successfully', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'session_token': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Invalid request',
            500: 'Server error'
        }
    )
    def post(self, request):
        serializer = PhoneSendVerificationSerializer(data=request.data)

        try:
            if not serializer.is_valid():
                return self.validation_error_response(
                    errors=serializer.errors,
                    message="Invalid phone verification data"
                )

            result = serializer.send_verification()
            return self.success_response(
                data=result,
                message="Verification code sent successfully"
            )

        except Exception as e:
            logging.error(f"Verification Send Error: {e}")
            return self.error_response(
                message="Verification process failed",
                errors={"details": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class RestaurantStaffViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantStaffSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RestaurantStaff.objects.filter(restaurant_id=self.kwargs['restaurant_pk'])

    @action(detail=False, methods=['GET'])
    def my_roles(self, request):
        roles = RestaurantStaff.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)
    

class BaseUserVerificationView(APIView):
    permission_classes = [AllowAny]
    verification_serializer_class = None

    def generate_tokens(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return access_token, refresh_token

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_user_serializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PhoneVerifySerializer,
        responses={
            200: 'Verification successful',
            400: 'Invalid request'
        }
    )
    def post(self, request):
        serializer = self.verification_serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.verify_code()
                access_token, refresh_token = self.generate_tokens(user)

                response = Response({
                    'message': 'Verification successful',
                    'user_id': user.id,
                    'refresh_token': refresh_token
                }, status=status.HTTP_200_OK)

                response.set_cookie(
                    key='access_token',
                    value=f"Bearer {access_token}",
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=15 * 60
                )
                return response

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class CustomerVerificationView(BaseUserVerificationView):
    verification_serializer_class = CustomerVerificationSerializer

    def get_user_serializer(self, user):
        from authentication.serializers import CustomerSerializer
        return CustomerSerializer(user.customer_profile)

class RestaurantStaffVerificationView(BaseUserVerificationView):
    verification_serializer_class = RestaurantStaffVerificationSerializer

    def get_user_serializer(self, user):
        return RestaurantStaffSerializer(
            user.staff_roles.filter(is_active=True),
            many=True
        )