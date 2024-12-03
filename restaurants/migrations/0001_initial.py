# Generated by Django 5.1.3 on 2024-12-03 15:34

import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='OpeningTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], unique=True)),
                ('from_hour', models.TimeField()),
                ('to_hour', models.TimeField()),
            ],
            options={
                'verbose_name': 'Opening Time',
                'verbose_name_plural': 'Opening Times',
                'ordering': ['weekday'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(help_text='Name on the bank account', max_length=200)),
                ('account_number', models.CharField(help_text='Bank account number', max_length=20, unique=True)),
                ('ifsc_code', models.CharField(help_text='Bank IFSC Code', max_length=11, validators=[django.core.validators.RegexValidator(message='Invalid IFSC Code', regex='^[A-Z]{4}0[A-Z0-9]{6}$')])),
                ('bank_name', models.CharField(help_text='Name of the Bank', max_length=200)),
                ('branch_name', models.CharField(blank=True, help_text='Bank Branch Name', max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Bank Account',
                'verbose_name_plural': 'Bank Accounts',
                'unique_together': {('account_number', 'ifsc_code')},
            },
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('CANTEEN', 'Canteen'), ('QUICK_SERVICE', 'Quick Service'), ('CASUAL_DINING', 'Casual Dining'), ('FINE_DINE', 'Fine Dine')], help_text='Select the restaurant category', max_length=20)),
                ('services', models.CharField(choices=[('DINE_IN', 'Dine-in'), ('TAKEAWAY', 'Takeaway')], help_text='Select available services', max_length=20)),
                ('cuisines', models.TextField(help_text='List of cuisines offered (comma-separated)')),
                ('name', models.CharField(help_text='Restaurant Name', max_length=200)),
                ('phone_number', models.CharField(help_text='Contact phone number', max_length=16, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('email', models.EmailField(help_text='Restaurant contact email', max_length=254, unique=True)),
                ('logo', models.ImageField(blank=True, help_text='Restaurant logo image', null=True, upload_to='restaurant_logos/')),
                ('fssai_license_number', models.CharField(help_text='Food Safety and Standards Authority of India License Number', max_length=50, unique=True)),
                ('gst_number', models.CharField(help_text='Goods and Services Tax Identification Number', max_length=15, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bank_accounts', models.ManyToManyField(help_text='Bank accounts associated with the restaurant', related_name='restaurants', to='restaurants.bankaccount')),
                ('location', models.ForeignKey(blank=True, help_text='Restaurant location details', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restaurants', to='restaurants.location')),
                ('opening_times', models.ManyToManyField(help_text='Restaurant operating hours for each day of the week', related_name='restaurants', to='restaurants.openingtime')),
            ],
            options={
                'verbose_name': 'Restaurant',
                'verbose_name_plural': 'Restaurants',
                'ordering': ['-created_at'],
            },
        ),
    ]
