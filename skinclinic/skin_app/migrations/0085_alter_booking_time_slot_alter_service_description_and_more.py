# Generated by Django 4.2.6 on 2024-04-04 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0084_timeslot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='time_slot',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='service',
            name='highlights',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='time_slot',
            field=models.CharField(max_length=100),
        ),
    ]
