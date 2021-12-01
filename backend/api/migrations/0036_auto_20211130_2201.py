# Generated by Django 3.0.5 on 2021-11-30 15:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20211130_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Минимум единица')], verbose_name='Количество ингредиента промежуточной модели'),
        ),
    ]