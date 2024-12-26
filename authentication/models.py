import random

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from restaurants.models import Restaurant
from zapeat import settings

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, role='receptionist', **extra_fields):
        if not mobile_number:
            raise ValueError("The mobile number must be set")
        if role not in dict(CustomUser.ROLE_CHOICES):
            raise ValueError(f"Invalid role: {role}")
        # extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(mobile_number=mobile_number, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'restaurant_admin')  # Default role for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('role') != 'restaurant_admin':
            raise ValueError("Superuser must have the role 'restaurant_admin'.")

        return self.create_user(mobile_number, password, **extra_fields)


class OTPVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()


class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.mobile_number

    @property
    def is_customer(self):
        """Check if user has a customer profile"""
        return hasattr(self, 'customer_profile')

    @property
    def is_restaurant_staff(self):
        """Check if user has any active restaurant staff roles"""
        return self.staff_roles.filter(is_active=True).exists()

    def get_staff_roles(self):
        """Get all active staff roles"""
        return self.staff_roles.filter(is_active=True)

    def get_active_restaurants(self):
        """Get all restaurants where user is an active staff member"""
        return [role.restaurant for role in self.get_staff_roles()]

    def is_restaurant_admin(self, restaurant_id):
        """Check if user is admin for a specific restaurant"""
        return self.staff_roles.filter(
            restaurant_id=restaurant_id,
            role='RESTAURANT_ADMIN',
            is_active=True
        ).exists()

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    default_address = models.TextField(blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)  # For storing food preferences, allergies, etc.
    favorite_restaurants = models.ManyToManyField(
        Restaurant,
        related_name='favorited_by',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer Profile - {self.user.mobile_number}"

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    @property
    def total_orders(self):
        return self.user.orders.count()

    @property
    def favorite_cuisines(self):
        return self.preferences.get('favorite_cuisines', [])


class RestaurantStaff(models.Model):
    STAFF_ROLES = [
        ('RESTAURANT_ADMIN', 'Restaurant Admin'),
        ('RESTAURANT_MANAGER', 'Restaurant Manager'),
        ('KITCHEN_STAFF', 'Kitchen Staff'),
        ('COUNTER_STAFF', 'Counter Staff'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_roles'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='staff_members'
    )
    role = models.CharField(max_length=20, choices=STAFF_ROLES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'restaurant']  # One role per restaurant per user

    def __str__(self):
        return f"{self.user.mobile_number} - {self.role} at {self.restaurant.name}"