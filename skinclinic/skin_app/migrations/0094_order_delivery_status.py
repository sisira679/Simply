# Generated by Django 4.2.6 on 2024-04-17 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0093_rename_recipient_message_receiver'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('OUT_FOR_DELIVERY', 'Out for Delivery'), ('DELIVERED', 'Delivered')], default='PENDING', max_length=20),
        ),
    ]