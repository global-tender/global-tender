# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0002_auto_20151214_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminars',
            name='event_is_active',
            field=models.BooleanField(default=True),
        ),
    ]
