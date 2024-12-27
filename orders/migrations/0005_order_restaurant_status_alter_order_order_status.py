# Generated by Django 5.1.3 on 2024-12-25 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_orderitem_customizations'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant_status',
            field=models.CharField(choices=[('RECEIVED', 'Received'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], default='RECEIVED', help_text='Status of the order from the restaurant', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('PREPARING', 'Preparing'), ('READY', 'Ready for Pickup/Delivery'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='PREPARING', help_text='Current status of the order', max_length=10),
        ),
    ]