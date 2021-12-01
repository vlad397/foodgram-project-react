# Generated by Django 3.0.5 on 2021-11-29 13:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20211129_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
