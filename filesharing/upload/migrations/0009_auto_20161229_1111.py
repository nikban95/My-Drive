# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0008_auto_20161229_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historyfile',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 29, 5, 41, 27, 645136, tzinfo=utc)),
        ),
    ]
