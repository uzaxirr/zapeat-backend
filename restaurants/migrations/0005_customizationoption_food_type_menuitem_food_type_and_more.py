# Generated by Django 5.1.3 on 2024-12-17 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0004_customizationgroup_customizationoption_menucategory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customizationoption',
            name='food_type',
            field=models.CharField(choices=[('VEG', 'Vegetarian'), ('NON-VEG', 'Non-Vegetarian'), ('EGG', 'Egg')], default=1, help_text='Select available food type', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='food_type',
            field=models.CharField(choices=[('VEG', 'Vegetarian'), ('NON-VEG', 'Non-Vegetarian'), ('EGG', 'Egg')], default='VEG', help_text='Select available food type', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='photo_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]