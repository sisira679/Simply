# Generated by Django 4.2.6 on 2024-02-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0024_remove_product_quality_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.AddField(
            model_name='product',
            name='quality',
            field=models.CharField(default=True, max_length=100),
        ),
    ]
