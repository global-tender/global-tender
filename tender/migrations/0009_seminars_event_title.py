# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-15 07:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0008_auto_20160619_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminars',
            name='event_title',
            field=models.CharField(blank=True, default=b'', max_length=1000, null=True),
        ),
    ]