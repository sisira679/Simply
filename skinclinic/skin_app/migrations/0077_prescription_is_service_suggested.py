# Generated by Django 4.2.6 on 2024-04-01 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0076_prescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='is_service_suggested',
            field=models.BooleanField(default=False),
        ),
    ]