import secrets
from datetime import datetime, timedelta

import jwt
from rest_framework import serializers
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number

from authentication.models import CustomUser, RestaurantStaff, Customer
from authentication.services import SMSService
from zapeat import settings

User = get_user_model()

class SessionTokenGenerator:
    """
    Utility class for generating and validating session tokens
    specific to OTP verification process.
    """
    @staticmethod
    def generate_token(mobile_number, verification_code):
        """
        Create a secure JWT token that:
        1. Includes phone number for verification
        2. Includes verification code for additional security
        3. Has a short expiration time
        """
        # Payload includes phone number and verification code
        payload = {
            'mobile_number': mobile_number,
            'session_code': verification_code,
            'exp': datetime.utcnow() + timedelta(minutes=10)  # Token expires in 10 minutes
        }

        # Use a secret key for signing (use settings.SECRET_KEY in production)
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def validate_token(token, mobile_number, verification_code):
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
                    payload['mobile_number'] == mobile_number and
                    payload['session_code'] == verification_code
            )
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

class PhoneSendVerificationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=20)

    def validate_mobile_number(self, value):
        """
        Comprehensive phone number validation:
        1. Parse using phonenumbers library
        2. Normalize to international format
        3. Validate number structure
        """
        try:
            mobile_number = parse(value, None)
            if not is_valid_number(mobile_number):
                raise serializers.ValidationError("Invalid phone number")

            # Normalize to international format
            normalized_number = f"+{mobile_number.country_code}{mobile_number.national_number}"
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
        mobile_number = self.validated_data['mobile_number']

        # Generate a secure verification code
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # Create or get user
        user, created = CustomUser.objects.get_or_create(
            mobile_number=mobile_number,
            defaults={'mobile_number': mobile_number}
        )


        # Initialize SMS service
        sms_service = SMSService()

        try:
            # Send verification SMS
            sms_sent = sms_service.send_verification_sms(
                mobile_number,
                verification_code
            )

            # Only proceed if SMS is sent successfully
            if sms_sent:
                # Generate session token with verification code
                session_token = SessionTokenGenerator.generate_token(
                    mobile_number,
                    verification_code
                )

                return {
                    'session_token': session_token,
                    'mobile_number': mobile_number
                }

        except ValueError as e:
            # Handle SMS sending errors
            raise serializers.ValidationError(str(e))

class PhoneVerifySerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=20)
    security_code = serializers.CharField(max_length=6)
    session_token = serializers.CharField(required=True)

    def validate_mobile_number(self, value):
        """
        Validate and normalize phone number
        """
        try:
            mobile_number = parse(value, None)
            return f"+{mobile_number.country_code}{mobile_number.national_number}"
        except Exception:
            raise serializers.ValidationError("Invalid phone number format")

    def verify_code(self):
        """
        Verification process:
        1. Validate session token
        2. Verify security code
        3. Mark user as verified
        """
        mobile_number = self.validated_data['mobile_number']
        security_code = self.validated_data['security_code']
        session_token = self.validated_data['session_token']

        # Validate the session token
        if not SessionTokenGenerator.validate_token(
                session_token,
                mobile_number,
                security_code
        ):
            raise serializers.ValidationError("Invalid or expired verification token")

        # Retrieve or create user
        try:
            user = User.objects.get(mobile_number=mobile_number)
            user.is_active = True  # Ensure user is active
            user.save()
            return user
        except User.DoesNotExist:
            # Create new user if doesn't exist
            user = User.objects.create(
                mobile_number=mobile_number,
                is_active=True
            )
            return user

class RestaurantStaffSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)  # Include the restaurant name in the output

    class Meta:
        model = RestaurantStaff
        fields = [
            'id',
            'mobile_number',
            'name',
            'role',
            'is_active',
            'restaurant',
            'restaurant_name',
        ]
        read_only_fields = ['id', 'restaurant_name']

    def validate_role(self, value):
        """Validate that the role is one of the allowed values."""
        valid_roles = [choice[0] for choice in RestaurantStaff.STAFF_ROLES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Choose from {valid_roles}.")
        return value

    def validate(self, attrs):
        """Custom validation for unique combination of user and restaurant."""
        mobile_number = attrs.get('mobile_number')
        restaurant = attrs.get('restaurant')

        if RestaurantStaff.objects.filter(mobile_number=mobile_number, restaurant=restaurant).exists():
            raise serializers.ValidationError("This staff member is already associated with this restaurant.")
        return attrs

class CustomerSerializer(serializers.ModelSerializer):
    favorite_restaurant_names = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'mobile_number',
            'name',
            'preferences',
            'is_active',
            'favorite_restaurants',
            'favorite_restaurant_names',
        ]
        read_only_fields = ['id', 'favorite_restaurant_names']

    def get_favorite_restaurant_names(self, obj):
        """
        Return a list of names for the favorite restaurants associated with the customer.
        """
        return [restaurant.name for restaurant in obj.favorite_restaurants.all()]

    def validate_preferences(self, value):
        """
        Validate the preferences field, ensuring it adheres to expected structure.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferences must be a dictionary.")
        # Add custom validations for specific keys if needed
        return value

    def validate(self, attrs):
        """
        Perform additional validations, if necessary.
        """
        return attrs

class CustomerVerificationSerializer(PhoneVerifySerializer):
    name = serializers.CharField(required=True)
    preferences = serializers.JSONField(required=False, default=dict)

    def verify_code(self):
        user = super().verify_code()
        
        # Create or get customer profile
        from django.utils import timezone
        customer, created = Customer.objects.get_or_create(
            customuser_ptr=user,
            defaults={
                'mobile_number': user.mobile_number,
                'name': self.validated_data['name'],
                'preferences': self.validated_data.get('preferences', {}),
                'is_active': True,
                'date_joined': timezone.now()  # Add this line
            }
        )
        
        return user

class RestaurantStaffVerificationSerializer(PhoneVerifySerializer):
    restaurant = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=RestaurantStaff.STAFF_ROLES, required=True)
    name = serializers.CharField(required=True)

    def verify_code(self):
        user = super().verify_code()
        
        # Create restaurant staff profile
        from django.utils import timezone
        staff, created = RestaurantStaff.objects.get_or_create(
            customuser_ptr=user,
            defaults={
                'mobile_number': user.mobile_number,
                'name': self.validated_data['name'],
                'role': self.validated_data['role'],
                'restaurant_id': self.validated_data['restaurant'],
                'is_active': True,
                'date_joined': timezone.now()
            }
        )
        
        # If staff exists, update their details
        if not created:
            staff.name = self.validated_data['name']
            staff.role = self.validated_data['role']
            staff.restaurant_id = self.validated_data['restaurant']
            staff.save()
        
        return user