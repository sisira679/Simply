# Generated by Django 4.2.6 on 2024-04-05 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0088_room_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='members',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='Room',
        ),
    ]
