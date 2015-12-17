# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0004_auto_20151217_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='fzs',
            name='sort',
            field=models.IntegerField(default=0),
        ),
    ]
