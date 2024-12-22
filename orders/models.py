from django.conf import settings
from django.db import models
from restaurants.models import MenuItem, Restaurant


class Order(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    ORDER_STATUS = [
        ('RECEIVED', 'Received'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup/Delivery'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Link to User model
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
        help_text="The user who placed the order"
    )

    # Restaurant reference
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Restaurant associated with the order"
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount for the order")
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='PENDING',
        help_text="Payment status of the order"
    )
    order_status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS,
        default='RECEIVED',
        help_text="Current status of the order"
    )
    special_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Additional instructions from the customer"
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the order was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated time of the order")

    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name} ({self.customer.mobile_number})"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",  # Changed related_name to avoid clash
        help_text="Order to which this item belongs"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="order_items",
        help_text="Menu item in the order"
    )
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of the item ordered")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the item at the time of order")
    # customizations = models.TextField(blank=True, null=True, help_text="Customizations applied to the item")

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity}) - Order #{self.order.id}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
