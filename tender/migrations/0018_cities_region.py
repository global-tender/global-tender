# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 11:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0017_auto_20160908_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='cities',
            name='region',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
