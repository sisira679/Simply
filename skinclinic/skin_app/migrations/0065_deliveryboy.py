# Generated by Django 4.2.6 on 2024-03-21 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0064_alter_product_skin_type_alter_skinconcern_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryBoy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
            ],
        ),
    ]
