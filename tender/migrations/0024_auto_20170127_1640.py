# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-27 13:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0023_promocode'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Promocode',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='region',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='seminar_type',
        ),
        migrations.RemoveField(
            model_name='fzs',
            name='allow_subscribe',
        ),
        migrations.DeleteModel(
            name='Subscribe',
        ),
    ]
