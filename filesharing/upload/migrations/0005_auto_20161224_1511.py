# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0004_auto_20161224_1509'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ['-lastModified']},
        ),
        migrations.AlterModelOptions(
            name='filepermission',
            options={'ordering': ['file']},
        ),
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ['-lastModified']},
        ),
        migrations.AlterModelOptions(
            name='folderpermission',
            options={'ordering': ['folder']},
        ),
    ]
