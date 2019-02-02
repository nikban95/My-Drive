# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0009_auto_20161229_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historyfile',
            name='lastModified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
