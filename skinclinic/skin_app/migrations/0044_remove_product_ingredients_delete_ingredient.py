# Generated by Django 4.2.6 on 2024-03-01 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0043_product_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='ingredients',
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
    ]
