# Generated by Django 4.2.6 on 2024-03-03 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0057_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='skin_app.OrderItem', to='skin_app.product'),
        ),
    ]
