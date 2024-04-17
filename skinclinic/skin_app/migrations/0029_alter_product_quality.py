# Generated by Django 4.2.6 on 2024-02-19 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0028_alter_product_quality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quality',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]