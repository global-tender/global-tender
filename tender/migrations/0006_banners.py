# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0005_fzs_sort'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banners',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('banner_name', models.CharField(max_length=1000)),
                ('click_count', models.IntegerField(default=0)),
                ('last_click', models.DateTimeField(null=True, verbose_name=b'last click date/time', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Banners',
            },
        ),
    ]
