# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000)),
                ('picture', models.CharField(max_length=1000)),
                ('posted', models.DateTimeField(verbose_name=b'date published')),
            ],
            options={
                'verbose_name': 'Citie',
            },
        ),
        migrations.CreateModel(
            name='FZs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'FZ',
            },
        ),
        migrations.CreateModel(
            name='Seminar_Programs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('program_short_name', models.CharField(max_length=50)),
                ('program_time_limit', models.CharField(max_length=1000)),
                ('program_top_title', models.CharField(max_length=1000, blank=True)),
                ('program_file', models.FileField(null=True, upload_to=b'seminar_programs/')),
            ],
            options={
                'verbose_name': 'Seminar_Program',
            },
        ),
        migrations.CreateModel(
            name='Seminars',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_date', models.DateTimeField(verbose_name=b'event date')),
                ('event_contact_phone', models.CharField(max_length=1000)),
                ('event_contact_name', models.CharField(max_length=1000)),
                ('event_contact_email', models.CharField(max_length=1000)),
                ('event_city', models.ForeignKey(to='tender.Cities')),
                ('event_fz', models.ForeignKey(to='tender.FZs')),
                ('event_program', models.ForeignKey(to='tender.Seminar_Programs')),
            ],
            options={
                'verbose_name': 'Seminar',
            },
        ),
    ]
