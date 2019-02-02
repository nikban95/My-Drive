from django.contrib import admin
# Register your models here.
from models import myUser, file, folder, folderClosure, historyFile
from models import filePermission, folderPermission
from models import notification, userNotification


admin.site.register(myUser)
admin.site.register(file)
admin.site.register(folder)
admin.site.register(folderClosure)
admin.site.register(filePermission)
admin.site.register(folderPermission)
admin.site.register(historyFile)
admin.site.register(notification)
admin.site.register(userNotification)
