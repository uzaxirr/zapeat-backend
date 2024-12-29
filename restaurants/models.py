from datetime import datetime
from geopy.distance import geodesic


from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from restaurants.base import BaseModel

# Weekdays Constant
WEEKDAYS = [
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
]

SPICE_LEVEL_CHOICES = [
    (1, 'Mild'),
    (2, 'Medium'),
    (3, 'Spicy')
]

SWEETNESS_LEVEL_CHOICES = [
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High')
]

class OpeningTime(models.Model):
    weekday = models.IntegerField(
        choices=WEEKDAYS,
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    def __str__(self):
        return f"{dict(WEEKDAYS)[self.weekday]} {self.from_hour}-{self.to_hour}"

    class Meta:
        verbose_name = "Opening Time"
        verbose_name_plural = "Opening Times"
        ordering = ['weekday']

class ItemAvailability(models.Model):
    weekday = models.IntegerField(
        choices=WEEKDAYS,
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    def __str__(self):
        return f"{dict(WEEKDAYS)[self.weekday]} {self.from_hour}-{self.to_hour}"

    class Meta:
        verbose_name = "Item Availability"
        verbose_name_plural = "Item Availabilities"
        ordering = ['weekday']

class BankAccount(models.Model):
    # Bank Account Type Choices
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', 'Savings Account'),
        ('CURRENT', 'Current Account'),
        ('CORPORATE', 'Corporate Account')
    ]

    # Account Name (Account Holder's Name)
    account_name = models.CharField(
        max_length=200,
        help_text="Name on the bank account"
    )

    # Account Number
    account_number = models.CharField(
        max_length=20,
        help_text="Bank account number"
    )

    # IFSC Code Validation
    ifsc_regex = RegexValidator(
        regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
        message="Invalid IFSC Code"
    )
    ifsc_code = models.CharField(
        max_length=11,
        validators=[ifsc_regex],
        help_text="Bank IFSC Code"
    )

    # Bank Name
    bank_name = models.CharField(
        max_length=200,
        help_text="Name of the Bank"
    )

    # Branch Name
    branch_name = models.CharField(
        max_length=200,
        help_text="Bank Branch Name",
        blank=True,
        null=True
    )

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} - {self.account_number}"

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        unique_together = ['account_number', 'ifsc_code']

class Location(models.Model):
    location = models.PointField(blank=True, null=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def distance_to(self, other_location):
        return geodesic(
            (self.latitude, self.longitude),
            (other_location.latitude, other_location.longitude)
        ).km


    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

class Restaurant(models.Model):
    # Category Choices
    CATEGORY_CHOICES = [
        ('CANTEEN', 'Canteen'),
        ('QUICK_SERVICE', 'Quick Service'),
        ('CASUAL_DINING', 'Casual Dining'),
        ('FINE_DINE', 'Fine Dine')
    ]

    SERVING_STYLE_CHOICES = [
        ('BUFFET', 'Buffet'),
        ('SELF_SERVICE', 'Self Service'),
        ('TABLE_SERVICE', 'Table Service')
    ]

    # Services Choices
    SERVICES_CHOICES = [
        ('DINE_IN', 'Dine-in'),
        ('TAKEAWAY', 'Takeaway')
    ]

    # Category Field
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Select the restaurant category"
    )

    service_style = models.CharField(
        max_length=20,
        choices=SERVING_STYLE_CHOICES,
        default='SELF_SERVICE',
        help_text="Select the restaurant serving style"
    )

    # Services Field (support multiple selections)
    services = models.CharField(
        max_length=20,
        choices=SERVICES_CHOICES,
        help_text="Select available services"
    )

    # Cuisines Field (allowing multiple cuisines)
    cuisines = models.TextField(
        help_text="List of cuisines offered (comma-separated)"
    )

    # Name Field
    name = models.CharField(
        max_length=200,
        help_text="Restaurant Name"
    )

    # Phone Number Validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    mobile_number = models.CharField(
        validators=[phone_regex],
        max_length=16,
        unique=True,
        help_text="Contact phone number"
    )

    # Email Field
    email = models.EmailField(
        unique=True,
        help_text="Restaurant contact email"
    )

    # Location Field
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='restaurants',
        help_text="Restaurant location details"
    )

    address = models.TextField(
        help_text="Restaurant address"
    )

    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text="Restaurant logo URL"
    )

    banner_url = models.URLField(
        blank=True,
        null=True,
        help_text="Restaurant banner URL"
    )

    # Opening Times Relationship
    opening_times = models.ManyToManyField(
        OpeningTime,
        related_name='restaurants',
        help_text="Restaurant operating hours for each day of the week",
    )

    # Bank Accounts Relationship
    bank_accounts = models.ManyToManyField(
        BankAccount,
        related_name='restaurants',
        help_text="Bank accounts associated with the restaurant"
    )

    # FSSAI License Number
    fssai_license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Food Safety and Standards Authority of India License Number"
    )

    # GST Number
    gst_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="Goods and Services Tax Identification Number"
    )

    seating_capacity = models.PositiveIntegerField(
        help_text="Number of seats available for dine-in customers",
        default=0
    )

    publicly_accessible = models.BooleanField(
        default=True,
        help_text="Check if the restaurant is publicly accessible"
    )

    organised_seating = models.BooleanField(
        default=False,
        help_text="Check if the restaurant has organised seating"
    )

    base_parcel_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Parcel charges for takeaway orders",
        default=0.0
    )

    additional_parcel_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Additional Parcel charges per item for takeaway orders",
        default=0.0
    )

    associated_pos = models.CharField(
        max_length=200,
        help_text="Associated POS system with the restaurant",
        blank=True,
        null=True
    )

    owner_name = models.CharField(
        max_length=200,
        help_text="Owner's Name",
        blank=True,
        null=True
    )

    owner_details = models.TextField(
        help_text="Owner's Contact Details",
        blank=True,
        null=True
    )

    kitchen_closing_time = models.TimeField(
        help_text="Kitchen closing time",
        blank=True,
        null=True
    )

    is_online = models.BooleanField(
        default=True,
        help_text="Check if the restaurant is currently open"
    )

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_open(self):
        now = datetime.now()
        current_weekday = now.weekday() + 1  # Monday=1
        current_time = now.time()

        return self.opening_times.filter(
            weekday=current_weekday,
            from_hour__lte=current_time,
            to_hour__gte=current_time
        ).exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['-created_at']

#TODO: Add Cuisine model

# class Cuisine(BaseModel):
#     name = models.CharField(max_length=200, unique=True)
#     restaurant = models.ForeignKey(
#         Restaurant,
#         on_delete=models.CASCADE,
#         related_name='cuisines',
#     )
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = 'Cuisine'
#         verbose_name_plural = 'Cuisines'
#         ordering = ['name']

# Menu Category (linked to Restaurant)
class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name="categories", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


# Menu Item (linked to MenuCategory)
class MenuItem(models.Model):
    FOOD_TYPE = [
        ('VEG', 'Vegetarian'),
        ('NON-VEG', 'Non-Vegetarian'),
        ('EGG', 'Egg')
    ]
    category = models.ForeignKey(MenuCategory, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customizable = models.BooleanField(default=False)
    photo_url = models.URLField(blank=True, null=True)
    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE,
        help_text="Select available food type"
    )
    spice_level = models.PositiveIntegerField(
        choices=SPICE_LEVEL_CHOICES,
        default=1,  # Default to Mild
        help_text="Select the spice level for this menu item (1 = Mild, 2 = Medium, 3 = Spicy)"
    )
    sweetness_level = models.PositiveIntegerField(
        choices=SWEETNESS_LEVEL_CHOICES,
        default=1,  # Default to Medium
        help_text="Select the sweetness level for this menu item (1 = Low, 2 = Medium, 3 = High)"
    )
    availability_times = models.ManyToManyField(
        ItemAvailability,
        related_name="menu_items",
        blank=True,
        help_text="Select the availability times for this menu item"
    )
    must_try = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.category.name}"


# Customization Group (linked to MenuItem)
class CustomizationGroup(models.Model):
    menu_item = models.ForeignKey(MenuItem, related_name="customization_groups", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    max_options_allowed = models.PositiveIntegerField(default=1)  # Max number of options allowed
    min_options_allowed = models.PositiveIntegerField(default=0)  # Min number of options allowed

    def __str__(self):
        return f"{self.name} - {self.menu_item.name}"


# Customization Option (linked to CustomizationGroup)
class CustomizationOption(models.Model):
    FOOD_TYPE = [
        ('VEG', 'Vegetarian'),
        ('NON-VEG', 'Non-Vegetarian'),
        ('EGG', 'Egg')
    ]
    group = models.ForeignKey(CustomizationGroup, related_name="options", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE,
        help_text="Select available food type"
    )
    spice_level = models.PositiveIntegerField(
        choices=SPICE_LEVEL_CHOICES,
        default=1,  # Default to Mild
        help_text="Select the spice level for this menu item (1 = Mild, 2 = Medium, 3 = Spicy)"
    )
    sweetness_level = models.PositiveIntegerField(
        choices=SWEETNESS_LEVEL_CHOICES,
        default=1,  # Default to Medium
        help_text="Select the sweetness level for this menu item (1 = Low, 2 = Medium, 3 = High)"
    )


def __str__(self):
        return f"{self.name} - {self.group.name}"

