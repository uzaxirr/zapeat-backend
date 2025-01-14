# Generated by Django 5.1.3 on 2024-12-18 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_customizationoption_food_type_menuitem_food_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='is_open',
            field=models.BooleanField(default=True, help_text='Check if the restaurant is currently open'),
        ),
    ]
