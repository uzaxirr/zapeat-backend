# Generated by Django 5.1.3 on 2024-12-22 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0009_itemavailability_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='restaurant',
            old_name='phone_number',
            new_name='mobile_number',
        ),
    ]