# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cities',
            name='picture',
            field=models.FileField(upload_to=b'city_pictures/'),
        ),
    ]
