# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-11 07:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0019_fzs_top_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Regions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Сайт: Регионы',
            },
        ),
        migrations.DeleteModel(
            name='Banners',
        ),
        migrations.RemoveField(
            model_name='cities',
            name='region',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='region',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='seminar_type',
        ),
    ]