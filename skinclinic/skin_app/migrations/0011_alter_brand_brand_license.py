# Generated by Django 4.2.6 on 2024-02-12 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0010_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='brand_license',
            field=models.TextField(),
        ),
    ]
