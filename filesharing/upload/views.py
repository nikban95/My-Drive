from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from forms import fileForm, myUserForm, userForm, shareForm
from models import myUser, file, folder, filePermission, folderPermission
from models import notification, userNotification, historyFile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.conf import settings
import os
import json
from django.db.models import Q, F
import mimetypes
import cStringIO
import zipfile
from django.utils.encoding import smart_str
from django.core.files.base import File
# Create your views here.


# Login related Views are below
def userRegisterView(request):
    currentuser = request.user
    if not currentuser.is_authenticated():
        if request.method == 'POST':
            myform = myUserForm(request.POST)
            form = userForm(request.POST)

            if form.is_valid() and myform.is_valid():
                # make the entry of user in db
                user1 = form.save(commit=False)
                user1.set_password(user1.password)
                user1.save()
                myuser1 = myform.save(commit=False)
                myuser1.user = user1
                myuser1.save()

                # login the user
                user1 = authenticate(
                    username=request.POST['username'],
                    password=request.POST['password'])
                login(request, user1)

                # create the user named folder in the db
                folder.createFolder(
                    name="Root",
                    owner=myuser1,
                    description="My Root Directory")

                return HttpResponseRedirect(reverse('mainpage'))
            else:
                # do nothing return the original form with errors in the end
                pass
        else:
            form = userForm()
            myform = myUserForm()

        data = {'form': form, 'myform': myform}
        return render(request, 'register.html', data)
    else:
        return HttpResponseRedirect(reverse('mainpage'))


def userLoginView(request):
    currentuser = request.user
    if not currentuser.is_authenticated():
        if request.method == 'POST':
            # authenticate the username and password
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                # if there is some other path to be reached after login
                if request.GET.get('next', None):
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect('/')
            else:
                data = {'loginfailed': True}
                return render(request, 'login.html', data)
        else:
            data = {'loginfailed': False}
            return render(request, 'login.html', data)
    else:
        return HttpResponseRedirect(reverse('mainpage'))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def userLogoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('mainpage'))


# main page view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def mainpageView(request):
    currentuser = request.user
    if currentuser.is_authenticated():
        return HttpResponseRedirect(reverse('myFiles'))
    else:
        return HttpResponseRedirect(reverse('login'))


# myfiles, shared with me, folder views below
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def myFilesView(request):
    currentUser = myUser.objects.get(user=request.user)
    # As all uploaded files will be in user root folder
    # get the root folder for user
    userRoot = folder.objects.filter(
        owner_id=currentUser.id,
        parent_id=F('id')).first()
    allFiles = file.objects.filter(parent=userRoot, trash=False)
    allFolders = folder.objects.filter(parent=userRoot, trash=False)
    allFilesPerm = ['O'] * allFiles.count()
    allFoldersPerm = ['O'] * allFolders.count()

    data = {
        'allFilesAndPerm': zip(allFiles, allFilesPerm),
        'allFoldersAndPerm': zip(allFolders, allFoldersPerm),
        'currentpage': "My Files",
        'shareForm': shareForm(),
    }
    return render(request, 'mainpage.html', data)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sharedWithMeView(request):
    currentUser = myUser.objects.get(user=request.user)

    allFilesPermObj = filePermission.objects.filter(
        Q(myUser=currentUser),
        Q(file__trash=False),
        Q(permission='R') | Q(permission='W')
    ).select_related('file')

    allFoldersPermObj = folderPermission.objects.filter(
        Q(myUser=currentUser),
        Q(folder__trash=False),
        Q(permission='R') | Q(permission='W')
    ).select_related('folder')

    data = {
        'allFilesPermObj': allFilesPermObj,
        'allFoldersPermObj': allFoldersPermObj,
        'currentpage': "Shared with me",
        'shareForm': shareForm(),
    }
    return render(request, 'mainpage.html', data)


def getPath(folderObj):
    tempFolder = folderObj
    path = []
    while (tempFolder.id != tempFolder.parent_id):
        tempFolder = tempFolder.parent
        path.append([tempFolder.id, tempFolder.name])
    # reverse the path list to get the path starting from root
    path.reverse()
    return path


def getPermissionAndPath(folderObj, currentUser):
    # check the folder permission and get path until permission folder
    folderObjPerm = None
    path = []
    while folderObj.id != folderObj.parent_id:
        folderObjPerm = folderPermission.objects.filter(
            myUser=currentUser,
            folder=folderObj).first()
        if folderObjPerm:
            break
        folderObj = folderObj.parent
        path.append([folderObj.id, folderObj.name])
    # reverse the path list to get the path
    path.reverse()

    if folderObjPerm:
        permission = folderObjPerm.permission
    else:
        permission = None
    return permission, path


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def folderView(request, folderId):
    currentUser = myUser.objects.get(user=request.user)
    folderObj = folder.objects.filter(id=folderId).first()

    if folderObj:
        parentTrash = folderObj.ancestors.filter(ancestorId__trash=True).exists()
        if (not parentTrash) and (not folderObj.trash):
            if folderObj.owner_id == currentUser.id:
                # current user is folder owner
                allFolders = folder.objects.filter(
                    parent=folderObj, trash=False)
                allFiles = file.objects.filter(parent=folderObj, trash=False)
                allFilesPerm = ['O'] * allFiles.count()
                allFoldersPerm = ['O'] * allFolders.count()

                # get the path of this folder
                path = getPath(folderObj)
                permission = 'O'
            else:
                permission, path = getPermissionAndPath(folderObj, currentUser)

                if permission:
                    if permission == 'D':
                        # not have the access to the folder
                        return render(request, '404.html')
                    else:
                        allFolders = folder.objects.filter(
                            parent=folderObj, trash=False)
                        allFiles = file.objects.filter(
                            parent=folderObj, trash=False)

                    # permission for all files in current folder
                        # files in the current folder with special permissions
                        newPermFiles = filePermission.objects.filter(
                            file__parent=folderObj,
                            file__trash=False,
                            myUser=currentUser)
                        newPermFilesCount = newPermFiles.count()

                        # make the permission list with updated permissions
                        index = 0
                        allFilesPerm = []
                        for f in allFiles:
                            if index == newPermFilesCount:
                                allFilesPerm.append(permission)
                                continue

                            if f.id == newPermFiles[index].file_id:
                                allFilesPerm.append(newPermFiles[index].permission)
                                index += 1
                            else:
                                allFilesPerm.append(permission)

                    # permission for all folders in current folder
                        # folders in the current folder with special permission
                        newPermFolders = folderPermission.objects.filter(
                            folder__parent=folderObj,
                            folder__trash=False,
                            myUser=currentUser).iterator()

                        # make the permission list with updated permissions
                        allFoldersPerm = []
                        newPermFinish = False
                        try:
                            newPerm = next(newPermFolders)
                        except StopIteration:
                            newPermFinish = True
                        for f in allFolders:
                            if newPermFinish:
                                allFoldersPerm.append(permission)
                                continue

                            if f.id == newPerm.folder_id:
                                allFoldersPerm.append(newPerm.permission)
                                try:
                                    newPerm = next(newPermFolders)
                                except StopIteration:
                                    newPermFinish = True
                            else:
                                allFoldersPerm.append(permission)

                else:
                    # not have access to the folder
                    return render(request, '404.html')
        else:
            # parent folder is trash
            return render(request, '404.html')

        data = {
            # permission is used to show/not show upload button
            'permission': permission,
            'currentFolder': folderObj,
            'allFilesAndPerm': zip(allFiles, allFilesPerm),
            'allFoldersAndPerm': zip(allFolders, allFoldersPerm),
            'path': path,
            'shareForm': shareForm(),
        }
        return render(request, 'mainpage.html', data)
    else:
        # folder doesnot exists return 404 page
        return render(request, '404.html')


def uploadFile(form, parentFolder, owner):
    myFile = form.save(commit=False)

    # remove invalid characters from filename
    tempName = smart_str(myFile.fileDb.name)
    invalidChars = "|:<>?;\"/\\"
    for char in invalidChars:
        tempName = tempName.replace(char, "_")
    myFile.name = tempName

    # set the parent folder
    myFile.parent = parentFolder

    # set the owner of file
    myFile.owner = owner

    # set the fileDb to none so as to create the file object
    # self.id is needed to save fileDb
    # thus it is updated later when file object has been created
    tempFile = myFile.fileDb
    myFile.fileDb = None
    myFile.save()
    myFile.fileDb = tempFile
    myFile.save()
    return myFile


# core functionality like upload, download, search views below
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def uploadFileView(request, folderId):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        form = fileForm(request.POST, request.FILES)
        if form.is_valid():
            if folderId:
                folderObj = folder.objects.filter(id=folderId).first()
                if folderObj:
                    if folderObj.owner == currentUser:
                        uf = uploadFile(form, folderObj, currentUser)
                        jsonObj = {
                            'success': 'File successfully uploaded.',
                        }
                        status = 200
                    else:
                        # check for permission
                        permission, path = getPermissionAndPath(
                            folderObj, currentUser)

                        if permission:
                            if permission == 'D':
                                # deny permission
                                jsonObj = {
                                    'error': 'Permission Denied.',
                                }
                                status = 400
                            elif permission == 'R':
                                # read permission i.e. no uploads can be done
                                jsonObj = {
                                    'error': 'Permission Denied.',
                                }
                                status = 400
                            elif permission == 'W':
                                # owner of file is same as owner of folder
                                owner = folderObj.owner
                                uf = uploadFile(form, folderObj, owner)
                                # it will get write permission by default
                                jsonObj = {
                                    'success': 'File successfully uploaded.'
                                }
                                status = 200
                        else:
                            # no permission is available
                            jsonObj = {
                                'error': 'Permission Denied.',
                            }
                            status = 400
                else:
                    # folder doesnot exists
                    jsonObj = {
                        'error': "Parent folder doesnot exists.",
                    }
                    status = 400
            else:
                # folderId is not present so upload at home
                userRootFolder = folder.objects.filter(
                    owner_id=currentUser.id,
                    parent_id=F('id')).first()
                owner = currentUser
                uf = uploadFile(form, userRootFolder, owner)
                jsonObj = {
                    'success': 'File successfully uploaded.'
                }
                status = 200
        else:
            # send form errors
            jsonObj = {
                'error': form.errors.items()[0][1].as_text(),
            }
            status = 400

        # my activity
        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="uploaded",
                objName=uf.name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


# currently searches only for owner files and shared with me files
# no internal folder searches on shared with me folders
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def searchView(request):
    currentUser = myUser.objects.filter(user=request.user)
    search = request.GET.get('q', "")

    # all Files
    # owner files
    allFiles = file.objects.filter(
        name__icontains=search,
        owner=currentUser,
        trash=False,
    )
    allFilesPerm = ['O'] * allFiles.count()

    # shared files
    allFilesPermObj = filePermission.objects.filter(
        Q(file__name__icontains=search),
        Q(file__trash=False),
        Q(myUser=currentUser, permission='R') |
        Q(myUser=currentUser, permission='W')
    ).select_related('file')

    # all folders
    # owner folders
    allFolders = folder.objects.filter(
        name__icontains=search,
        owner=currentUser,
        trash=False,
    )
    allFoldersPerm = ['O'] * allFolders.count()

    # shared folders
    allFoldersPermObj = folderPermission.objects.filter(
        Q(folder__name__icontains=search),
        Q(folder__trash=False),
        Q(myUser=currentUser, permission='R') |
        Q(myUser=currentUser, permission='W')
    ).select_related('folder')

    data = {
        'allFilesAndPerm': zip(allFiles, allFilesPerm),
        'allFoldersAndPerm': zip(allFolders, allFoldersPerm),
        'allFilesPermObj': allFilesPermObj,
        'allFoldersPermObj': allFoldersPermObj,
        'currentpage': "Search",
        'shareForm': shareForm(),
    }
    return render(request, 'mainpage.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def createFolderView(request, folderId):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        name = smart_str(request.POST.get('foldername', None))
        # name remove invalid chars
        invalidChars = "|:<>?;\"/\\"
        for char in invalidChars:
            name = name.replace(char, "_")

        if name:
            if folderId:
                folderObj = folder.objects.filter(id=folderId).first()
                if folderObj:
                    if folderObj.owner == currentUser:
                        newFol = folder.createFolder(name, folderObj.owner, folderObj)
                        jsonObj = {
                            'success': 'Folder created successfully.',
                        }
                        status = 200
                    else:
                        # check for permission
                        permission, path = getPermissionAndPath(
                            folderObj, currentUser)

                        if permission:
                            if permission == 'D':
                                # deny permission
                                jsonObj = {
                                    'error': 'Permission Denied.',
                                }
                                status = 200
                            elif permission == 'R':
                                # read permission i.e. no folder can be made
                                jsonObj = {
                                    'error': 'Permission Denied.',
                                }
                                status = 200
                            elif permission == 'W':
                                # owner of folder is same as owner of parent
                                owner = folderObj.owner
                                newFol = folder.createFolder(name, folderObj.owner, folderObj)
                                jsonObj = {
                                    'success': 'Folder created successfully.'
                                }
                                status = 200
                        else:
                            # no permission is available
                            jsonObj = {
                                'error': 'Permission Denied.',
                            }
                            status = 200
                else:
                    # folder doesnot exists
                    jsonObj = {
                        'error': "Parent folder doesnot exists.",
                    }
                    status = 200
            else:
                # folderId is not present so make folder at home
                userRootFolder = folder.objects.filter(
                    owner_id=currentUser.id,
                    parent_id=F('id')).first()
                owner = currentUser
                newFol = folder.createFolder(name, owner, userRootFolder)
                jsonObj = {
                    'success': 'Folder created successfully.'
                }
                status = 200
        else:
            # send form errors
            jsonObj = {
                'error': "Empty Name Field.",
            }
            status = 200

        # my activity
        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="created folder",
                objName=newFol.name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def renameView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        name = smart_str(request.POST.get('newname', None))
        if obj and name:
            objType, objId = obj.split('-')
            try:
                objId = int(objId)
            except:
                objId = None

            # name remove invalid chars
            invalidChars = "|:<>?;\"/\\"
            for char in invalidChars:
                name = name.replace(char, "_")

            if objType == "folder" and objId:
                folderObj = folder.objects.filter(id=objId).first()
                if folderObj:
                    if folderObj.owner_id == currentUser.id:
                        oldName = folderObj.name
                        folderObj.name = name
                        folderObj.lastModified = timezone.now()
                        folderObj.save()
                        jsonObj = {
                            'success': "Rename successful.",
                        }
                        status = 200
                    else:
                        jsonObj = {
                            'error': "Permission Denied.",
                        }
                        status = 200
                else:
                    jsonObj = {
                        'error': "Folder doesnot exists.",
                    }
                    status = 200
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                if fileObj:
                    if fileObj.owner_id == currentUser.id:
                        oldName = fileObj.name
                        fileObj.name = name
                        fileObj.lastModified = timezone.now()
                        fileObj.save()
                        jsonObj = {
                            'success': "Rename successful.",
                        }
                        status = 200
                    else:
                        jsonObj = {
                            'error': "Permission Denied.",
                        }
                        status = 200
                else:
                    jsonObj = {
                        'error': "File doesnot exists.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Empty name or no file selected.",
            }
            status = 200

        # my activity
        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="renamed " + oldName + " to",
                objName=name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def changeDescriptionView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        description = request.POST.get('newdesc', None)
        if obj and description:
            objType, objId = obj.split('-')
            try:
                objId = int(objId)
            except:
                objId = None
            if objType == "folder" and objId:
                folderObj = folder.objects.filter(id=objId).first()
                if folderObj:
                    if folderObj.owner_id == currentUser.id:
                        objName = folderObj.name
                        folderObj.description = description
                        folderObj.save()
                        jsonObj = {
                            'success': "Description changed",
                        }
                        status = 200
                    else:
                        permission, path = getPermissionAndPath(
                            folderObj,
                            currentUser)
                        if permission == 'W':
                            objName = folderObj.name
                            folderObj.description = description
                            folderObj.save()
                            jsonObj = {
                                'success': "Description changed",
                            }
                            status = 200
                        else:
                            jsonObj = {
                                'error': "Permission Denied.",
                            }
                            status = 200
                else:
                    jsonObj = {
                        'error': "Folder doesnot exists.",
                    }
                    status = 200
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                if fileObj:
                    if fileObj.owner_id == currentUser.id:
                        objName = fileObj.name
                        fileObj.description = description
                        fileObj.save()
                        jsonObj = {
                            'success': "Description changed.",
                        }
                        status = 200
                    else:
                        permFileObj = filePermission.objects.filter(
                            myUser_id=currentUser.id,
                            file_id=fileObj.id
                        ).first()
                        if permFileObj:
                            # permission on file exists
                            permission = permFileObj.permission
                            if permission == "W":
                                # file has write permission
                                objName = fileObj.name
                                fileObj.description = description
                                fileObj.save()
                                jsonObj = {
                                    'success': "Description changed.",
                                }
                                status = 200
                            else:
                                # permission on file is deny or read
                                return render(request, '404.html')
                        else:
                            # permission on file is not found
                            # so check permission of parent folder
                            permissionParent, path = getPermissionAndPath(
                                fileObj.parent, currentUser)
                            if permissionParent == "W":
                                # file has write permission
                                objName = fileObj.name
                                fileObj.description = description
                                fileObj.save()
                                jsonObj = {
                                    'success': "Description changed.",
                                }
                                status = 200
                            else:
                                # permission on file is deny or read
                                return render(request, '404.html')
                else:
                    jsonObj = {
                        'error': "File doesnot exists.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Empty description or no file selected.",
            }
            status = 200

        # my activity
        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="changed description of",
                objName=objName,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


def downloadFile(fileObj):
    response = HttpResponse()
    response['Content-Type'] = ""
    response['mimetype'] = mimetypes.guess_type(
        fileObj.fileDb.path, strict=True)
    response['Content-Disposition'] = 'attachment; filename="%s";' % smart_str(fileObj.name)
    response['X-Sendfile'] = smart_str(fileObj.fileDb.path)
    return response


def addFolderToZip(zipFile, folderObj, currentUser, zipSubdir):
    zipSubdir = os.path.join(zipSubdir, smart_str(folderObj.name))

    files = file.objects.filter(
        parent=folderObj,
        trash=False,
    ).exclude(
        permittedUsers__myUser=currentUser,
        permittedUsers__permission="D"
    )

    for f in files:
        # Calculate path for file in zip
        zipPath = os.path.join(zipSubdir, smart_str(f.name))

        # Add file, at correct path
        zipFile.write(f.fileDb.path, zipPath)

    folders = folder.objects.filter(
        parent=folderObj,
        trash=False,
    ).exclude(
        permittedUsers__myUser=currentUser,
        permittedUsers__permission="D"
    )

    for f in folders:
        if f.id == folderObj.id:
            continue
        addFolderToZip(zipFile, f, currentUser, zipSubdir)


def downloadFolder(folderObj, currentUser):
    # Open StringIO to grab in-memory ZIP contents
    s = cStringIO.StringIO()
    # The zip compressor
    zipFile = zipfile.ZipFile(s, "w")

    # add files of this folder to zip and also of child folders
    addFolderToZip(zipFile, folderObj, currentUser, "")

    # Must close zip for all contents to be written
    zipFile.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue())
    resp['Content-Type'] = "application/x-zip-compressed"
    # ..and correct content-disposition
    zipName = smart_str(folderObj.name) + ".zip"
    resp['Content-Disposition'] = 'attachment; filename="%s"' % zipName

    return resp


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def downloadView(request):
    if request.method == "POST":
        currentUser = myUser.objects.get(user=request.user)
        obj = request.POST.get('obj', None)
        objType, objId = obj.split('-')
        try:
            objId = int(objId)
        except:
            objId = None

        if objType == "folder" and objId:
            folderObj = folder.objects.filter(id=objId).first()
            if folderObj:
                parentTrash = folderObj.ancestors.filter(
                    ancestorId__trash=True).exists()
                if folderObj.trash or parentTrash:
                    # folder is trash or parent is trash
                    return render(request, '404.html')
                else:
                    if folderObj.owner_id == currentUser.id:
                        # owner of folder
                        return downloadFolder(folderObj, currentUser)
                    else:
                        # permission on folder
                        permission, path = getPermissionAndPath(
                            folderObj, currentUser)
                        if permission == "R" or permission == "W":
                            # file has read or write permission
                            return downloadFolder(folderObj, currentUser)
                        else:
                            # permission on file is deny
                            return render(request, '404.html')
            else:
                # file doesnot exists
                return render(request, '404.html')
        elif objType == "file" and objId:
            fileObj = file.objects.filter(id=objId).first()
            if fileObj:
                parentTrash = fileObj.parent.ancestors.filter(
                    ancestorId__trash=True).exists()
                if parentTrash or fileObj.trash:
                    # this file is trash or parent folder is trashed
                    return render(request, '404.html')
                else:
                    if fileObj.owner_id == currentUser.id:
                        # owner of file
                        return downloadFile(fileObj)
                    else:
                        permFileObj = filePermission.objects.filter(
                            myUser_id=currentUser.id,
                            file_id=fileObj.id
                        ).first()
                        if permFileObj:
                            # permission on file exists
                            permission = permFileObj.permission
                            if permission == "R" or permission == "W":
                                # file has read or write permission
                                return downloadFile(fileObj)
                            else:
                                # permission on file is deny
                                return render(request, '404.html')
                        else:
                            # permission on file is not found
                            # so check permission of parent folder
                            permissionParent, path = getPermissionAndPath(
                                fileObj.parent, currentUser)
                            if permissionParent == "R" or permissionParent == "W":
                                # file has read or write permission
                                return downloadFile(fileObj)
                            else:
                                # permission on file is deny
                                return render(request, '404.html')
            else:
                # file doesnot exists
                return render(request, '404.html')
        else:
            # invalid objtype/id
            return render(request, '404.html')
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def trashView(request):
    currentUser = myUser.objects.get(user=request.user)
    allFiles = file.objects.filter(owner_id=currentUser.id, trash=True)
    allFolders = folder.objects.filter(owner_id=currentUser.id, trash=True)
    allFilesPerm = ['O'] * allFiles.count()
    allFoldersPerm = ['O'] * allFolders.count()

    data = {
        'allFilesAndPerm': zip(allFiles, allFilesPerm),
        'allFoldersAndPerm': zip(allFolders, allFoldersPerm),
        'currentpage': "Trash",
    }
    return render(request, 'mainpage.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def deleteView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        objType, objId = obj.split('-')
        try:
            objId = int(objId)
        except:
            objId = None
        if objType == "folder" and objId:
            folderObj = folder.objects.filter(id=objId).first()
            if folderObj:
                name = folderObj.name
                if folderObj.owner_id == currentUser.id:
                    folderObj.trash = True
                    folderObj.lastModified = timezone.now()
                    folderObj.save()
                    jsonObj = {
                        'success': "Delete successful.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Folder doesnot exists.",
                }
                status = 200
        elif objType == "file" and objId:
            fileObj = file.objects.filter(id=objId).first()
            if fileObj:
                name = fileObj.name
                if fileObj.owner_id == currentUser.id:
                    fileObj.trash = True
                    fileObj.lastModified = timezone.now()
                    fileObj.save()
                    jsonObj = {
                        'success': "Delete successful.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "File doesnot exists.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Undefined object type/id.",
            }
            status = 200

        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="deleted",
                objName=name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def deleteForeverView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        objType, objId = obj.split('-')
        try:
            objId = int(objId)
        except:
            objId = None
        if objType == "folder" and objId:
            folderObj = folder.objects.filter(id=objId).first()
            if folderObj:
                if folderObj.owner_id == currentUser.id:
                    folderObj.delete()
                    jsonObj = {
                        'success': "Folder deleted permanently.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Folder doesnot exists.",
                }
                status = 200
        elif objType == "file" and objId:
            fileObj = file.objects.filter(id=objId).first()
            if fileObj:
                if fileObj.owner_id == currentUser.id:
                    fileObj.delete()
                    jsonObj = {
                        'success': "File deleted permanently.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "File doesnot exists.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Undefined object type/id.",
            }
            status = 200

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def restoreDeletedFileView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        objType, objId = obj.split('-')
        try:
            objId = int(objId)
        except:
            objId = None
        if objType == "folder" and objId:
            folderObj = folder.objects.filter(id=objId).first()
            if folderObj:
                name = folderObj.name
                if folderObj.owner_id == currentUser.id:
                    folderObj.trash = False
                    folderObj.lastModified = timezone.now()
                    folderObj.save()
                    jsonObj = {
                        'success': "Restore successful.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Folder doesnot exists.",
                }
                status = 200
        elif objType == "file" and objId:
            fileObj = file.objects.filter(id=objId).first()
            if fileObj:
                name = fileObj.name
                if fileObj.owner_id == currentUser.id:
                    fileObj.trash = False
                    fileObj.lastModified = timezone.now()
                    fileObj.save()
                    jsonObj = {
                        'success': "Restore successful.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "File doesnot exists.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Undefined object type/id.",
            }
            status = 200

        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="restored",
                objName=name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


def shareFile(fileObj, usernames, access):
    successUsers = []
    failUsers = []
    usernames = usernames.split(',')
    for username in usernames:
        username = username.strip(' ')
        user = myUser.objects.filter(user__username=username).first()
        if user:
            if user.id == fileObj.owner_id:
                pass
            else:
                filePermission.objects.update_or_create(
                    file=fileObj, myUser=user,
                    defaults={'permission': access})
            successUsers.append(user)
        else:
            failUsers.append(username)
    return successUsers, failUsers


def shareFolder(folderObj, usernames, access):
    successUsers = []
    failUsers = []
    usernames = usernames.split(',')
    for username in usernames:
        username = username.strip(' ')
        user = myUser.objects.filter(user__username=username).first()
        if user:
            if user.id == folderObj.owner_id:
                pass
            else:
                folderPermission.objects.update_or_create(
                    folder=folderObj,
                    myUser=user,
                    defaults={'permission': access})
                folderPermission.objects.filter(
                    myUser=user,
                    folder__ancestors__ancestorId_id=folderObj.id,
                ).delete()
                filePermission.objects.filter(
                    myUser=user,
                    file__parent__ancestors__ancestorId_id=folderObj.id,
                ).delete()
            successUsers.append(user)
        else:
            failUsers.append(username)
    return successUsers, failUsers


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def shareView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        usernames = request.POST.get('usernames', None)
        access = request.POST.get('access', None)
        if obj and usernames and (access == 'R' or access == 'W' or access == 'D'):
            objType, objId = obj.split('-')
            try:
                objId = int(objId)
            except:
                objId = None
            if objType == "folder" and objId:
                folderObj = folder.objects.filter(id=objId).first()
                if folderObj:
                    name = folderObj.name
                    owner = folderObj.owner
                    if folderObj.owner_id == currentUser.id:
                        successUsers, failUsers = shareFolder(
                            folderObj, usernames, access)
                        jsonObj = {
                            'successUsers': successUsers,
                            'failUsers': failUsers,
                        }
                        status = 200
                    else:
                        permission, path = getPermissionAndPath(
                            folderObj,
                            currentUser)
                        if permission == 'W':
                            successUsers, failUsers = shareFolder(
                                folderObj, usernames, access)
                            jsonObj = {
                                'successUsers': successUsers,
                                'failUsers': failUsers,
                            }
                            status = 200
                        else:
                            jsonObj = {
                                'error': "Permission Denied.",
                            }
                            status = 200
                else:
                    jsonObj = {
                        'error': "Folder doesnot exists.",
                    }
                    status = 200
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                owner = fileObj.owner
                if fileObj:
                    name = fileObj.name
                    if fileObj.owner_id == currentUser.id:
                        successUsers, failUsers = shareFile(
                            fileObj, usernames, access)
                        jsonObj = {
                            'successUsers': successUsers,
                            'failUsers': failUsers,
                        }
                        status = 200
                    else:
                        permFileObj = filePermission.objects.filter(
                            myUser_id=currentUser.id,
                            file_id=fileObj.id
                        ).first()
                        if permFileObj:
                            # permission on file exists
                            permission = permFileObj.permission
                            if permission == "W":
                                # file has write permission
                                successUsers, failUsers = shareFile(
                                    fileObj, usernames, access)
                                jsonObj = {
                                    'successUsers': successUsers,
                                    'failUsers': failUsers,
                                }
                                status = 200
                            else:
                                # permission on file is deny or read
                                return render(request, '404.html')
                        else:
                            # permission on file is not found
                            # so check permission of parent folder
                            permissionParent, path = getPermissionAndPath(
                                fileObj.parent, currentUser)
                            if permissionParent == "W":
                                # file has write permission
                                successUsers, failUsers = shareFile(
                                    fileObj, usernames, access)
                                jsonObj = {
                                    'successUsers': successUsers,
                                    'failUsers': failUsers,
                                }
                                status = 200
                            else:
                                # permission on file is deny or read
                                return render(request, '404.html')
                else:
                    jsonObj = {
                        'error': "File doesnot exists.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Empty usernames or no file selected.",
            }
            status = 200

        # my activity
        successUserNames = []
        if 'successUsers' in jsonObj:
            for user in successUsers:
                note = notification.objects.create(
                    actor=currentUser,
                    verb="shared(" + access + ")",
                    objName=name,
                    actorDest=user,
                )
                userNotification.objects.create(
                    note=note,
                    notifiedUser=user,
                )
                userNotification.objects.create(
                    note=note,
                    notifiedUser=owner,
                )
                # username to send as json
                successUserNames.append(user.user.username)

            jsonObj = {
                'successUsers': successUserNames,
                'failUsers': failUsers,
            }

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


def updateFile(fileObj, fileDb):
    # create history file without fileDb
    hf = historyFile.objects.create(
        description=fileObj.description,
        lastModified=timezone.now(),
        historyOf=fileObj,
    )
    # generate the path
    newPath = os.path.join(
        settings.MEDIA_ROOT,
        str(fileObj.id),
        str(fileObj.id) + "-" + str(hf.lastModified),
    )
    # rename the old file
    os.rename(fileObj.fileDb.path, newPath)
    # assign the old file to history model
    hf.fileDb = newPath
    hf.save()

    # assign new file to fileObj
    fileObj.fileDb = fileDb
    fileObj.lastModified = timezone.now()
    fileObj.save()


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def updateView(request):
    if request.method == "POST":
        currentUser = myUser.objects.get(user=request.user)
        obj = request.POST.get('obj', None)
        objType, objId = obj.split('-')
        try:
            objId = int(objId)
        except:
            objId = None

        form = fileForm(request.POST, request.FILES)
        if form.is_valid():
            if objType == "folder" and objId:
                # folder updation not done
                jsonObj = {
                    'error': "Select a file to update.",
                }
                status = 400
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                if fileObj:
                    name = fileObj.name
                    owner = fileObj.owner
                    if fileObj.owner_id == currentUser.id:
                        # owner of file
                        updateFile(fileObj, request.FILES['fileDb'])
                        jsonObj = {
                            'success': "Update successful.",
                        }
                        status = 200
                    else:
                        permFileObj = filePermission.objects.filter(
                            myUser_id=currentUser.id,
                            file_id=fileObj.id
                        ).first()
                        if permFileObj:
                            # permission on file exists
                            permission = permFileObj.permission
                            if permission == "W":
                                # file has read or write permission
                                updateFile(fileObj, request.FILES['fileDb'])
                                jsonObj = {
                                    'success': "Update successful.",
                                }
                                status = 200
                            else:
                                # permission on file is deny
                                jsonObj = {
                                    'error': "Permission denied.",
                                }
                                status = 400
                        else:
                            # permission on file is not found
                            # so check permission of parent folder
                            permissionParent, path = getPermissionAndPath(
                                fileObj.parent, currentUser)
                            if permissionParent == "W":
                                # file has read or write permission
                                updateFile(fileObj, request.FILES['fileDb'])
                                jsonObj = {
                                    'success': "Update successful.",
                                }
                                status = 200
                            else:
                                # permission on file is deny
                                jsonObj = {
                                    'error': "Permission denied.",
                                }
                                status = 400
                else:
                    # file doesnot exists
                    jsonObj = {
                        'error': "Selected file doesnot exist.",
                    }
                    status = 400
            else:
                # invalid objtype/id
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 400
        else:
            # file size > 10MB
            jsonObj = {
                'error': "Max File Size exceeded.",
            }
            status = 400

        if 'success' in jsonObj:
            note = notification.objects.create(
                actor=currentUser,
                verb="updated",
                objName=name,
            )
            userNotification.objects.create(
                note=note,
                notifiedUser=owner,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        # get request not allowed
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def manageVersionsView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        if obj:
            objType, objId = obj.split('-')
            try:
                objId = int(objId)
            except:
                objId = None
            if objType == "folder" and objId:
                jsonObj = {
                    'error': 'No versions for folder.'
                }
                status = 200
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                if fileObj:
                    if fileObj.owner_id == currentUser.id:
                        versions = fileObj.myOldVersions.all()
                        data = {
                            'fileObj': fileObj,
                            'versions': versions,
                        }
                        return render(request, 'manage-versions-modal.html', data)
                    else:
                        jsonObj = {
                            'error': "Permission Denied.",
                        }
                        status = 200
                else:
                    jsonObj = {
                        'error': "File doesnot exists.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "No file selected.",
            }
            status = 200

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        return render(request, '404.html')


def downloadVersionFile(versionObj):
    response = HttpResponse()
    response['Content-Type'] = ""
    response['mimetype'] = mimetypes.guess_type(
        versionObj.fileDb.path, strict=True)
    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(versionObj.historyOf.name)
    response['X-Sendfile'] = smart_str(versionObj.fileDb.path)
    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def versionDownloadView(request):
    if request.method == "POST":
        currentUser = myUser.objects.get(user=request.user)
        versionId = request.POST.get('versionId', None)
        try:
            versionId = int(versionId)
        except:
            versionId = None

        if versionId:
            versionObj = historyFile.objects.filter(
                id=versionId
            ).select_related('historyOf').first()
            if versionObj:
                if versionObj.historyOf.owner_id == currentUser.id:
                    # owner of file
                    return downloadVersionFile(versionObj)
                else:
                    # only owner can download versions
                    return render(request, '404.html')
            else:
                # version doesnot exists
                return render(request, '404.html')
        else:
            # invalid invalid versionId
            return render(request, '404.html')
    else:
        # get request not allowed
        return render(request, '404.html')


def restoreVersionFile(versionObj):
    fileObj = versionObj.historyOf
    fileDb = versionObj.fileDb

    # create history file without fileDb
    hf = historyFile.objects.create(
        description=fileObj.description,
        lastModified=timezone.now(),
        historyOf=fileObj,
    )
    # generate the path
    newPath = os.path.join(
        settings.MEDIA_ROOT,
        str(fileObj.id),
        str(fileObj.id) + "-" + str(hf.lastModified),
    )
    # rename the old file
    os.rename(fileObj.fileDb.path, newPath)
    # assign the old file to history model
    hf.fileDb = newPath
    hf.save()

    # assign new file to fileObj
    fileObj.fileDb = File(fileDb)
    fileObj.description = versionObj.description + " (Restored File)"
    fileObj.lastModified = timezone.now()
    fileObj.save()


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def versionRestoreView(request):
    if request.method == 'POST':
        currentUser = myUser.objects.get(user=request.user)
        versionId = request.POST.get('versionId', None)
        try:
            versionId = int(versionId)
        except:
            versionId = None

        if versionId:
            versionObj = historyFile.objects.filter(
                id=versionId
            ).select_related('historyOf').first()
            if versionObj:
                name = versionObj.historyOf.name
                if versionObj.historyOf.owner_id == currentUser.id:
                    # owner of file
                    restoreVersionFile(versionObj)
                    jsonObj = {
                        'success': "File restored successfully.",
                    }
                    status = 200
                else:
                    jsonObj = {
                        'error': "Permission Denied.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Version doesnot exist.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "Version doesnot exist.",
            }
            status = 200

        if 'success' in jsonObj:
            notification.objects.create(
                actor=currentUser,
                verb="restored old version of",
                objName=name,
            )

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        return render(request, '404.html')


# obj is either a file or folder
def getAllUsersPermission(obj):
    userPermissions = {}
    while obj.id != obj.parent_id:
        users = obj.permittedUsers.all().select_related('myUser__user')
        for u in users:
            if u.user.username in userPermissions:
                pass
            else:
                userPermissions[u.user.username] = u.permission
        obj = obj.parent

    return userPermissions


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def viewPermissionsView(request):
    currentUser = myUser.objects.get(user=request.user)
    if request.method == 'POST':
        obj = request.POST.get('obj', None)
        if obj:
            objType, objId = obj.split('-')
            try:
                objId = int(objId)
            except:
                objId = None
            if objType == "folder" and objId:
                folderObj = folder.objects.filter(id=objId).first()
                if folderObj:
                    if folderObj.owner_id == currentUser.id:
                        userPermissions = getAllUsersPermission(folderObj)
                        data = {
                            'obj': folderObj,
                            'userPermissions': userPermissions,
                        }
                        return render(request, 'view-permissions-modal.html', data)
                    else:
                        jsonObj = {
                            'error': "Permission Denied.",
                        }
                        status = 200
                else:
                    jsonObj = {
                        'error': "Folder doesnot exists.",
                    }
                    status = 200
            elif objType == "file" and objId:
                fileObj = file.objects.filter(id=objId).first()
                if fileObj:
                    if fileObj.owner_id == currentUser.id:
                        userPermissions = getAllUsersPermission(fileObj)
                        data = {
                            'obj': fileObj,
                            'userPermissions': userPermissions,
                        }
                        return render(request, 'view-permissions-modal.html', data)
                    else:
                        jsonObj = {
                            'error': "Permission Denied.",
                        }
                        status = 200
                else:
                    jsonObj = {
                        'error': "File doesnot exists.",
                    }
                    status = 200
            else:
                jsonObj = {
                    'error': "Undefined object type.",
                }
                status = 200
        else:
            jsonObj = {
                'error': "No file selected.",
            }
            status = 200

        jsonObj = json.dumps(jsonObj)
        mimetype = 'application/json'
        return HttpResponse(jsonObj, mimetype, status=status)
    else:
        return render(request, '404.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def notificationView(request):
    currentUser = myUser.objects.get(user=request.user)
    notifications = currentUser.myNotifications.all().select_related(
        'note__actor__user', 'note__actorDest__user')
    data = {
        'currentpage': 'Notifications',
        'notifications': notifications,
    }
    return render(request, 'notification.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def getNewNotificationCountJsonView(request):
    currentUser = myUser.objects.get(user=request.user)
    count = userNotification.objects.filter(
        notifiedUser=currentUser,
        new=True).count()

    count = {'count': count}
    data = json.dumps(count)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def getNewNotificationView(request):
    currentUser = myUser.objects.get(user=request.user)
    notifications = userNotification.objects.filter(
        notifiedUser=currentUser, new=True)

    # done as due to lazy propagation if notifications is send as data then
    # the data send will have query executed after update instruction
    notification = [n for n in notifications]

    # make the new field of all user notifications to be false
    notifications.update(new=False)

    data = {'notifications': notification}
    return render(request, 'notification_ajax.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def getNotificationView(request):
    currentUser = myUser.objects.get(user=request.user)
    newNotificationCount = currentUser.myNotifications.filter(new=True).count()
    notifications = currentUser.myNotifications.all()
    if 5 > newNotificationCount:
        notification = notifications[:5]
    else:
        notification = notifications[:newNotificationCount]

    # make the new field of all user notifications to be false
    notifications.update(new=False)

    data = {'notifications': notification}
    return render(request, 'notification_ajax.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def getActivityView(request):
    currentUser = myUser.objects.get(user=request.user)
    activity = currentUser.myActivity.all()[:5]

    data = {
        'activities': activity,
    }
    return render(request, 'activity_ajax.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def activityView(request):
    currentUser = myUser.objects.get(user=request.user)
    activity = currentUser.myActivity.all().select_related(
        'actorDest__user')

    data = {
        'currentpage': "My Activity",
        'activities': activity,
    }
    return render(request, 'activity.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def getUsernameJsonView(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        usernames = myUser.objects.filter(user__username__istartswith=q)[:5]
        result = []

        for user in usernames:
            user_json = {}
            # user_json['first_name'] = user.user.first_name
            # user_json['last_name'] = user.user.last_name
            user_json['value'] = user.user.username
            result.append(user_json)

        data = json.dumps(result)
    else:
        data = 'fail'

    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
