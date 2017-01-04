# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 08:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cah', '0009_auto_20161218_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(through='cah.PlayerGame', to='cah.Player'),
        ),
    ]