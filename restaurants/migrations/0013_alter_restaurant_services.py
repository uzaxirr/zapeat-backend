# Generated by Django 5.1.3 on 2024-12-29 16:20

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0012_remove_restaurant_logo_restaurant_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='services',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('DINE_IN', 'Dine-in'), ('TAKEAWAY', 'Takeaway')], max_length=20), default=list, help_text='Select available services (can select multiple)', size=None),
        ),
    ]