# Generated by Django 4.2.1 on 2023-05-11 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_userdevice'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdevice',
            old_name='user_id',
            new_name='user',
        ),
    ]
