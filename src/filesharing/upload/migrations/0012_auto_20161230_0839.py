# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import upload.models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0011_auto_20161229_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='file',
        ),
        migrations.AddField(
            model_name='notification',
            name='objName',
            field=upload.models.TruncatingCharField(max_length=30, blank=True),
        ),
    ]
