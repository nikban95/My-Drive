# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import upload.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='file',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fileDb', models.FileField(upload_to=upload.models.uploadDest)),
                ('name', models.CharField(max_length=30, blank=True)),
                ('description', models.CharField(max_length=500, blank=True)),
                ('lastModified', models.DateTimeField(default=django.utils.timezone.now)),
                ('trash', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['lastModified'],
            },
        ),
        migrations.CreateModel(
            name='filePermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.IntegerField(default=2, choices=[(0, b'Deny'), (1, b'Read'), (2, b'Write')])),
                ('file', models.ForeignKey(related_name='permittedUsers', to='upload.file', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, blank=True)),
                ('description', models.CharField(max_length=500, blank=True)),
                ('lastModified', models.DateTimeField(default=django.utils.timezone.now)),
                ('trash', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['lastModified'],
            },
        ),
        migrations.CreateModel(
            name='folderClosure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ancestorId', models.ForeignKey(related_name='descendantFolders', to='upload.folder', null=True)),
                ('folderId', models.ForeignKey(related_name='ancestors', to='upload.folder', null=True)),
            ],
            options={
                'ordering': ['folderId', 'ancestorId'],
            },
        ),
        migrations.CreateModel(
            name='folderPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.IntegerField(default=2, choices=[(0, b'Deny'), (1, b'Read'), (2, b'Write')])),
                ('folder', models.ForeignKey(related_name='permittedUsers', to='upload.folder', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='myUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verb', models.CharField(max_length=30, blank=True)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('actor', models.ForeignKey(related_name='myActivity', to='upload.myUser', null=True)),
                ('actorDest', models.ForeignKey(related_name='activityWithMe', to='upload.myUser', null=True)),
                ('file', models.ForeignKey(to='upload.file', null=True)),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='userNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('new', models.BooleanField(default=True)),
                ('note', models.ForeignKey(related_name='notificationUsers', to='upload.notification', null=True)),
                ('notifiedUser', models.ForeignKey(related_name='myNotifications', to='upload.myUser', null=True)),
            ],
            options={
                'ordering': ['note'],
            },
        ),
        migrations.AddField(
            model_name='folderpermission',
            name='myUser',
            field=models.ForeignKey(related_name='permittedFolders', to='upload.myUser', null=True),
        ),
        migrations.AddField(
            model_name='folder',
            name='owner',
            field=models.ForeignKey(related_name='myFolders', to='upload.myUser', null=True),
        ),
        migrations.AddField(
            model_name='folder',
            name='parent',
            field=models.ForeignKey(related_name='childFolders', to='upload.folder', null=True),
        ),
        migrations.AddField(
            model_name='filepermission',
            name='myUser',
            field=models.ForeignKey(related_name='permittedFiles', to='upload.myUser', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(related_name='myFiles', to='upload.myUser', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='parent',
            field=models.ForeignKey(related_name='childFiles', to='upload.folder', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='folderpermission',
            unique_together=set([('myUser', 'folder')]),
        ),
        migrations.AlterUniqueTogether(
            name='folderclosure',
            unique_together=set([('folderId', 'ancestorId')]),
        ),
        migrations.AlterUniqueTogether(
            name='filepermission',
            unique_together=set([('myUser', 'file')]),
        ),
    ]
