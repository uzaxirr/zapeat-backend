from django.db import models
from django.contrib.auth.models import AbstractUser

# class User(AbstractUser):
#     ROLE_CHOICES = [
#         ('CUSTOMER', 'Customer'),
#         ('RESTAURANT_OWNER', 'Restaurant Owner'),
#     ]
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
#
#     def is_customer(self):
#         return self.role == 'CUSTOMER'
#
#     def is_restaurant_owner(self):
#         return self.role == 'RESTAURANT_OWNER'
