# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 07:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cah', '0005_auto_20161218_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='host',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='_game_host', to='cah.Player'),
        ),
    ]
