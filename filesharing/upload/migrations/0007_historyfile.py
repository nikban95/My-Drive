# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import upload.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0006_auto_20161225_1923'),
    ]

    operations = [
        migrations.CreateModel(
            name='historyFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fileDb', models.FileField(upload_to=upload.models.historyDest)),
                ('description', upload.models.TruncatingCharField(max_length=500, blank=True)),
                ('lastModified', models.DateTimeField(default=datetime.datetime(2016, 12, 29, 5, 40, 5, 181086, tzinfo=utc))),
                ('historyOf', models.ForeignKey(to='upload.file', null=True)),
            ],
            options={
                'ordering': ['historyOf', '-lastModified'],
            },
        ),
    ]
