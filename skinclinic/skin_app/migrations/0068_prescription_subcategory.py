# Generated by Django 4.2.6 on 2024-03-31 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0067_alter_prescription_medicine'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='subcategory',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, to='skin_app.subcategory'),
        ),
    ]