# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import upload.models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0005_auto_20161224_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='description',
            field=upload.models.TruncatingCharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=upload.models.TruncatingCharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='filepermission',
            name='permission',
            field=upload.models.TruncatingCharField(default=b'R', max_length=1, choices=[(b'D', b'Deny'), (b'R', b'Read'), (b'W', b'Write')]),
        ),
        migrations.AlterField(
            model_name='folder',
            name='description',
            field=upload.models.TruncatingCharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='name',
            field=upload.models.TruncatingCharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='folderpermission',
            name='permission',
            field=upload.models.TruncatingCharField(default=b'R', max_length=1, choices=[(b'D', b'Deny'), (b'R', b'Read'), (b'W', b'Write')]),
        ),
        migrations.AlterField(
            model_name='notification',
            name='verb',
            field=upload.models.TruncatingCharField(max_length=30, blank=True),
        ),
    ]
