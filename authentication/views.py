import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import login

from authentication.serializers import PhoneVerifySerializer, PhoneSendVerificationSerializer


class SendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

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

    def post(self, request):
        serializer = PhoneVerifySerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.verify_code()
                return Response({
                    'message': 'Phone number verified successfully',
                    'user_id': user.id,
                    'is_verified': user.is_phone_verified
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )