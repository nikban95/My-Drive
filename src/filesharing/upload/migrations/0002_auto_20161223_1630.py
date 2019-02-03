# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filepermission',
            name='permission',
            field=models.CharField(default=b'R', max_length=1, choices=[(b'D', b'Deny'), (b'R', b'Read'), (b'W', b'Write')]),
        ),
        migrations.AlterField(
            model_name='folderpermission',
            name='permission',
            field=models.CharField(default=b'R', max_length=1, choices=[(b'D', b'Deny'), (b'R', b'Read'), (b'W', b'Write')]),
        ),
    ]
