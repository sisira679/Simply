# Generated by Django 4.2.6 on 2024-03-30 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0066_deliveryuser_delete_deliveryboy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescription',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='skin_app.product'),
        ),
    ]