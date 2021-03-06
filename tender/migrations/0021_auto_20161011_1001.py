# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-11 07:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0020_auto_20161011_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='cities',
            name='region',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tender.Regions'),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='region',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tender.Regions'),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='seminar_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tender.FZs'),
        ),
    ]
