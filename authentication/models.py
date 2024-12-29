from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from restaurants.models import Restaurant

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("The Mobile Number must be set")
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(mobile_number, password, **extra_fields)

    def get_by_natural_key(self, mobile_number):
        return self.get(mobile_number=mobile_number)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.mobile_number


class CustomerManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("The Phone Number must be set")
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Customer(CustomUser):
    name = models.CharField(max_length=100)
    preferences = models.JSONField(default=dict, blank=True)  # For storing food preferences, allergies, etc.
    favorite_restaurants = models.ManyToManyField(
        Restaurant,
        related_name='favorited_by',
        blank=True
    )

    # USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['name']

    objects = CustomerManager()

    def __str__(self):
        return f"Customer - {self.mobile_number}"

    @property
    def favorite_cuisines(self):
        return self.preferences.get('favorite_cuisines', [])


class RestaurantStaffManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("The Phone Number must be set")
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class RestaurantStaff(CustomUser):
    STAFF_ROLES = [
        ('RESTAURANT_ADMIN', 'Restaurant Admin'),
        ('RESTAURANT_MANAGER', 'Restaurant Manager'),
        ('KITCHEN_STAFF', 'Kitchen Staff'),
        ('COUNTER_STAFF', 'Counter Staff'),
    ]
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=STAFF_ROLES)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='staff_members'
    )

    REQUIRED_FIELDS = ['name']

    objects = RestaurantStaffManager()

    # class Meta:
    #     unique_together = ['user', 'restaurant']  # One role per restaurant per user

    def __str__(self):
        return f"{self.mobile_number} - {self.role} at {self.restaurant.name}"
