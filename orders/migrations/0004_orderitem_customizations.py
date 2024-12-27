# Generated by Django 5.1.3 on 2024-12-23 19:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_order_delivery_address_and_more'),
        ('restaurants', '0010_rename_phone_number_restaurant_mobile_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='customizations',
            field=models.ForeignKey(blank=True, help_text='Customizations applied to the item', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items_customization', to='restaurants.customizationoption'),
        ),
    ]