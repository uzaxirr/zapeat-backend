import secrets
from datetime import datetime, timedelta

import jwt
from rest_framework import serializers
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number

from authentication.services import SMSService
from zapeat import settings

User = get_user_model()

class SessionTokenGenerator:
    """
    Utility class for generating and validating session tokens
    specific to OTP verification process.
    """
    @staticmethod
    def generate_token(phone_number, verification_code):
        """
        Create a secure JWT token that:
        1. Includes phone number for verification
        2. Includes verification code for additional security
        3. Has a short expiration time
        """
        # Payload includes phone number and verification code
        payload = {
            'phone_number': phone_number,
            'session_code': verification_code,
            'exp': datetime.utcnow() + timedelta(minutes=10)  # Token expires in 10 minutes
        }

        # Use a secret key for signing (use settings.SECRET_KEY in production)
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def validate_token(token, phone_number, verification_code):
        """
        Validate the session token by checking:
        1. Token is not expired
        2. Phone number matches
        3. Verification code matches
        """
        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Validate phone number and verification code
            return (
                    payload['phone_number'] == phone_number and
                    payload['session_code'] == verification_code
            )
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

class PhoneSendVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        """
        Comprehensive phone number validation:
        1. Parse using phonenumbers library
        2. Normalize to international format
        3. Validate number structure
        """
        try:
            phone_number = parse(value, None)
            if not is_valid_number(phone_number):
                raise serializers.ValidationError("Invalid phone number")

            # Normalize to international format
            normalized_number = f"+{phone_number.country_code}{phone_number.national_number}"
            return normalized_number
        except Exception:
            raise serializers.ValidationError("Invalid phone number format")

    def send_verification(self):
        """
        Enhanced verification process with Twilio SMS:
        1. Generate secure verification code
        2. Create/retrieve user
        3. Send SMS via Twilio
        4. Generate session token
        """
        phone_number = self.validated_data['phone_number']

        # Generate a secure verification code
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # Create or get user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'phone_number': phone_number}
        )

        # Initialize SMS service
        sms_service = SMSService()

        try:
            # Send verification SMS
            sms_sent = sms_service.send_verification_sms(
                phone_number,
                verification_code
            )

            # Only proceed if SMS is sent successfully
            if sms_sent:
                # Generate session token with verification code
                session_token = SessionTokenGenerator.generate_token(
                    phone_number,
                    verification_code
                )

                return {
                    'session_token': session_token,
                    'phone_number': phone_number
                }

        except ValueError as e:
            # Handle SMS sending errors
            raise serializers.ValidationError(str(e))

class PhoneVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    security_code = serializers.CharField(max_length=6)
    session_token = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        """
        Validate and normalize phone number
        """
        try:
            phone_number = parse(value, None)
            return f"+{phone_number.country_code}{phone_number.national_number}"
        except Exception:
            raise serializers.ValidationError("Invalid phone number format")

    def verify_code(self):
        """
        Verification process:
        1. Validate session token
        2. Verify security code
        3. Mark user as verified
        """
        phone_number = self.validated_data['phone_number']
        security_code = self.validated_data['security_code']
        session_token = self.validated_data['session_token']

        # Validate the session token
        if not SessionTokenGenerator.validate_token(
                session_token,
                phone_number,
                security_code
        ):
            raise serializers.ValidationError("Invalid or expired verification token")

        # Retrieve user
        try:
            user = User.objects.get(phone_number=phone_number)
            user.is_phone_verified = True
            user.save()
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")