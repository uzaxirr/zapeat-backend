# Generated by Django 5.1.3 on 2024-12-29 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0011_rename_is_open_restaurant_is_online'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='logo',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='address',
            field=models.TextField(default='mere laude pe', help_text='Restaurant address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='banner_url',
            field=models.URLField(blank=True, help_text='Restaurant banner URL', null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='logo_url',
            field=models.URLField(blank=True, help_text='Restaurant logo URL', null=True),
        ),
    ]
