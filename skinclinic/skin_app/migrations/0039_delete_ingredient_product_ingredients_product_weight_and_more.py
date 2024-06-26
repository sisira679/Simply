# Generated by Django 4.2.6 on 2024-02-29 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skin_app', '0038_ingredient'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Ingredient',
        ),
        migrations.AddField(
            model_name='product',
            name='ingredients',
            field=models.ManyToManyField(blank=True, choices=[('ingredient1', 'Ingredient 1'), ('ingredient2', 'Ingredient 2'), ('ingredient3', 'Ingredient 3'), ('ingredient4', 'Ingredient 4')], to='skin_app.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.CharField(default=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='age_limit',
            field=models.CharField(choices=[('above_10', 'Above 10'), ('below_5', 'Below 5'), ('above_18', 'Above 18'), ('above_15', 'Above 15'), ('below_12', 'Below 12'), ('above_21', 'Above 21'), ('all', 'All')], default=True, max_length=50),
        ),
    ]
