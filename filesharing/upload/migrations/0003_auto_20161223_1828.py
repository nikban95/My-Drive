# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0002_auto_20161223_1630'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filepermission',
            options={'ordering': ['file']},
        ),
        migrations.AlterModelOptions(
            name='folderpermission',
            options={'ordering': ['folder']},
        ),
    ]
