# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0010_auto_20161229_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historyfile',
            name='historyOf',
            field=models.ForeignKey(related_name='myOldVersions', to='upload.file', null=True),
        ),
    ]
