# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-04 11:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0018_cities_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='fzs',
            name='top_description',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
