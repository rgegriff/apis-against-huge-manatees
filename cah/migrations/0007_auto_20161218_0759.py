# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 07:59
from __future__ import unicode_literals

from django.db import migrations
import positions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cah', '0006_auto_20161218_0742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='position',
            field=positions.fields.PositionField(default=-1, null=True),
        ),
    ]