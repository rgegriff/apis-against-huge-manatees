# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 06:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import positions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cah', '0002_auto_20161218_0510'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', positions.fields.PositionField(default=-1)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cah.Card')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cah.Player')),
            ],
        ),
        migrations.AlterField(
            model_name='game',
            name='game_state',
            field=models.CharField(choices=[('starting', 'Starting'), ('pick_wc', 'Waiting for Players To Pick White Cards'), ('pick_win', 'Waiting for Card Czar to Pick Winner'), ('game_over', 'Game Over')], default='starting', max_length=3),
        ),
        migrations.AddField(
            model_name='player',
            name='current_play',
            field=models.ManyToManyField(related_name='_player_play', through='cah.PlayCard', to='cah.Card'),
        ),
    ]
