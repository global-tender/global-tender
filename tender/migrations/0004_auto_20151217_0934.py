# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0003_seminars_event_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seminar_programs',
            name='program_file',
            field=models.FileField(null=True, upload_to=b'seminar_programs/', blank=True),
        ),
    ]
