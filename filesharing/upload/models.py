from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.mail import send_mail
from django.conf import settings
import shutil
# Create your models here.


class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField, self).get_prep_value(value)
        if value:
            return value[:self.max_length]
        return value


class myUser(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.username


class folder(models.Model):
    name = TruncatingCharField(max_length=30, blank=True)
    parent = models.ForeignKey(
        'self',
        related_name='childFolders',
        null=True)
    owner = models.ForeignKey(
        'myUser',
        related_name='myFolders',
        null=True)
    description = TruncatingCharField(max_length=500, blank=True)
    lastModified = models.DateTimeField(default=timezone.now)
    trash = models.BooleanField(default=False)

    class Meta:
        ordering = ['-lastModified']

    # if the parent is not given it will create a folder with parent as itself
    # it is used to create root folder for each user
    @staticmethod
    def createFolder(name, owner, parent=None, description=""):
        # create the folder
        fol = folder.objects.create()
        fol.name = name
        fol.parent = parent
        fol.owner = owner
        fol.description = description
        fol.save()

        # if parent not given, make it parent of itself
        if not parent:
            # set parent
            fol.parent = fol
            fol.save()
        else:
            # make closure for ancestors
            # create closure instance for folder and parent
            folderClosure.objects.create(folderId=fol, ancestorId=parent)

            # create closures for ancestors of folder
            closures = folderClosure.objects.filter(folderId=parent)
            for t in closures:
                # we have set id to none so to create new instances and not update the previous ones
                t.id = None
                t.folderId = fol
            folderClosure.objects.bulk_create(closures)
        return fol

    def __unicode__(self):
        return str(self.id) + " " + self.name + " " + str(self.parent.id)


class folderClosure(models.Model):
    folderId = models.ForeignKey(
        folder,
        related_name='ancestors',
        null=True)
    ancestorId = models.ForeignKey(
        folder,
        related_name='descendantFolders',
        null=True)

    class Meta:
        unique_together = ('folderId', 'ancestorId')
        ordering = ['folderId', 'ancestorId']

    def __unicode__(self):
        return str(self.ancestorId.id) + " ancestor of " + str(self.folderId.id)


def uploadDest(self, fileName):
    return os.path.join(settings.MEDIA_ROOT, str(self.id), str(self.id))


# to create a file,
# first create file model without fileDb
# then assign the fileDb because to assign it self.id is needed
class file(models.Model):
    fileDb = models.FileField(upload_to=uploadDest)
    name = TruncatingCharField(max_length=30, blank=True)
    parent = models.ForeignKey(
        folder,
        related_name='childFiles',
        null=True)
    owner = models.ForeignKey(
        'myUser',
        related_name='myFiles',
        null=True)
    description = TruncatingCharField(max_length=500, blank=True)
    lastModified = models.DateTimeField(default=timezone.now)
    trash = models.BooleanField(default=False)

    class Meta:
        ordering = ['-lastModified']

    def __unicode__(self):
        return str(self.id) + " " + self.name + " " + str(self.parent.id)


@receiver(post_save, sender=folder)
@receiver(post_save, sender=file)
def updateLastModified(sender, instance, **kwargs):
    parent = instance.parent
    if ((instance != parent) and (parent)):
        parent.lastModified = timezone.now()
        parent.save()


@receiver(post_delete, sender=file)
def deleteFileOnDisk(sender, instance, **kwargs):
    path = os.path.join(settings.MEDIA_ROOT, str(instance.id))
    if os.path.exists(path):
        shutil.rmtree(path)


PERMISSION = (
    # always start the values from 0
    ('D', 'Deny'),
    ('R', 'Read'),
    ('W', 'Write'),
)


class filePermission(models.Model):
    myUser = models.ForeignKey(
        myUser,
        related_name='permittedFiles',
        null=True,
    )
    file = models.ForeignKey(
        file,
        related_name='permittedUsers',
        null=True,
    )
    permission = TruncatingCharField(
        max_length=1,
        choices=PERMISSION,
        default='R',
    )

    class Meta:
        unique_together = ('myUser', 'file')
        ordering = ['file']

    def __unicode__(self):
        return self.myUser.user.username + " " + str(self.file.id)


class folderPermission(models.Model):
    myUser = models.ForeignKey(
        myUser,
        related_name='permittedFolders',
        null=True,
    )
    folder = models.ForeignKey(
        folder,
        related_name='permittedUsers',
        null=True,
    )
    permission = TruncatingCharField(
        max_length=1,
        choices=PERMISSION,
        default='R',
    )

    class Meta:
        unique_together = ('myUser', 'folder')
        ordering = ['folder']

    def __unicode__(self):
        return self.myUser.user.username + " " + str(self.folder.id)


def historyDest(self, fileName):
    return os.path.join(
        settings.MEDIA_ROOT,
        str(self.historyOf_id),
        str(self.historyOf_id) + "-" + str(self.lastModified),
    )


class historyFile(models.Model):
    fileDb = models.FileField(upload_to=historyDest)
    description = TruncatingCharField(max_length=500, blank=True)
    lastModified = models.DateTimeField(default=timezone.now)
    historyOf = models.ForeignKey(
        file,
        related_name='myOldVersions',
        null=True
    )

    class Meta:
        ordering = ['historyOf', '-lastModified']

    def __unicode__(self):
        return str(self.historyOf_id) + "file with time " + str(self.lastModified)


class notification(models.Model):
    # action performed by
    actor = models.ForeignKey(
        myUser,
        null=True,
        related_name='myActivity')
    # what action performed
    verb = TruncatingCharField(max_length=30, blank=True)
    # targetfilename of action
    objName = TruncatingCharField(max_length=30, blank=True)
    # action performed on/with
    actorDest = models.ForeignKey(
        myUser,
        null=True,
        related_name='activityWithMe')
    # time of action
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-time']

    def __unicode__(self):
        return self.actor.user.username + " " + self.verb + " " + str(self.objName)


class userNotification(models.Model):
    notifiedUser = models.ForeignKey(
        myUser,
        related_name='myNotifications',
        null=True)
    note = models.ForeignKey(
        notification,
        related_name='notificationUsers',
        null=True)
    new = models.BooleanField(default=True)

    class Meta:
        ordering = ['note']

    def __unicode__(self):
        return self.notifiedUser.user.username + " notified"


@receiver(post_save, sender=userNotification)
def sendNotificationMail(sender, instance, **kwargs):
    if kwargs.get('created', None):
        fileName = instance.note.objName
        subject = "Notification: " + fileName
        note = instance.note
        emailReceiver = instance.notifiedUser.user.email
        message = "<b>" + note.actor.user.username + "</b> has " + note.verb + " " + "<b>" + fileName + "</b> file";
        if note.actorDest:
            message += " with "
            if instance.notifiedUser == note.actorDest:
                message += "you."
            else:
                message += note.actorDest.user.username
        else:
            message += "."

        # send mail is used to send mail
        # html_message is used to interpret message as html
        try:
            send_mail(
                subject,
                "",
                settings.EMAIL_HOST_USER,
                [emailReceiver],
                html_message=message)
        except Exception as e:
            print("Error ocuured in sending mail to " + emailReceiver)
            print(e)

# example of sending a template as mail
# from django.template.loader import render_to_string
# msg_plain = render_to_string('templates/email.txt', {'some_params': some_params})
# msg_html = render_to_string('templates/email.html', {'some_params': some_params})

# send_mail(
#     'email title',
#     msg_plain,
#     'some@sender.com',
#     ['some@receiver.com'],
#     html_message=msg_html,
# )
