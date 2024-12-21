# Generated by Django 5.1.3 on 2024-12-21 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_rename_mobile_number_customuser_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('restaurant_admin', 'Restaurant Admin'), ('boh_staff', 'BOH Staff'), ('manager', 'Manager'), ('foh_staff', 'FOH Staff'), ('receptionist', 'Receptionist')], default='receptionist', max_length=20),
        ),
    ]
