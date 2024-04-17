# Generated by Django 4.2.6 on 2024-02-12 05:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0003_doctorprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Specializations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specializations', models.CharField(blank=True, choices=[('medical_dermatology', 'Medical Dermatology'), ('cosmetic_dermatology', 'Cosmetic Dermatology'), ('laser_dermatology', 'Laser Dermatology'), ('hair_treatment', 'Hair Treatment')], max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specializations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
