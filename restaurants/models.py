from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

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
    phone_number = models.CharField(
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

    # Restaurant Logo
    logo = models.ImageField(
        upload_to='restaurant_logos/',
        null=True,
        blank=True,
        help_text="Restaurant logo image"
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

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['-created_at']