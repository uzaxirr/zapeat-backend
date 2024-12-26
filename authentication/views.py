import logging
from datetime import datetime, timedelta

import jwt
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from authentication.models import RestaurantStaff
from authentication.serializers import PhoneVerifySerializer, PhoneSendVerificationSerializer, RestaurantStaffSerializer
from zapeat import settings


class SendVerificationCodeView(APIView):
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
            if serializer.is_valid():
                result = serializer.send_verification()
                return Response(
                    {'session_token': result['session_token']},
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # Comprehensive error logging and response
            logging.error(f"Verification Send Error: {e}")
            return Response(
                {'error': 'Verification process failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyPhoneView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PhoneVerifySerializer,
        responses={
            200: openapi.Response('Phone verified successfully', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Invalid request'
        }
    )
    def post(self, request):
        serializer = PhoneVerifySerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.verify_code()

                # Generate tokens
                access_token_expiration = datetime.utcnow() + timedelta(minutes=15)
                refresh_token_expiration = datetime.utcnow() + timedelta(days=7)

                access_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'exp': access_token_expiration
                    },
                    settings.SECRET_KEY,
                    algorithm='HS256'
                )

                refresh_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'exp': refresh_token_expiration
                    },
                    settings.SECRET_KEY,
                    algorithm='HS256'
                )

                # Set access token as a secure HTTP-only cookie
                response = Response({
                    'message': 'Phone number verified successfully',
                    'user_id': user.id,
                    'is_verified': user.is_phone_verified,
                    'refresh_token': refresh_token  # Include refresh token in the response body
                }, status=status.HTTP_200_OK)

                # Add the access token to cookies
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,  # Set to False in development, True in production
                    samesite='Strict',  # Adjust based on your application's requirements
                    max_age=15 * 60  # 15 minutes in seconds
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