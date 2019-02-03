"""filesharing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from upload import views
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/$', views.userRegisterView, name='register'),
    url(r'^login/$', views.userLoginView, name='login'),
    url(r'^logout/$', views.userLogoutView, name='logout'),
    url(r'^$', views.mainpageView, name='mainpage'),
    url(r'^my-files/$', views.myFilesView, name='myFiles'),
    url(r'^folder/(?P<folderId>\d+)$', views.folderView),
    url(r'^shared-with-me/$', views.sharedWithMeView, name='shared-with-me'),
    url(r'^search/$', views.searchView, name='search'),
    url(r'^uploadFile/(?P<folderId>\d*)$', views.uploadFileView),
    url(r'^createfolder/(?P<folderId>\d*)$', views.createFolderView),
    url(r'^rename/$', views.renameView, name="rename"),
    url(r'^chngdesc/$', views.changeDescriptionView, name="changeDescription"),
    url(r'^download/$', views.downloadView, name='download'),
    url(r'^trash/$', views.trashView, name='trash'),
    url(r'^delete/$', views.deleteView, name='delete'),
    url(r'^delete-forever/$', views.deleteForeverView, name="delete-forever"),
    url(r'^restore-delete/$', views.restoreDeletedFileView, name="restore-delete"),
    url(r'^get/username/$', views.getUsernameJsonView, name='getusername'),
    url(r'^share/$', views.shareView, name='share'),
    url(r'^update/$', views.updateView, name='update'),
    url(r'^manage-versions/$', views.manageVersionsView),
    url(r'^version-download/$', views.versionDownloadView),
    url(r'^version-restore/$', views.versionRestoreView),
    url(r'^view-permissions/$', views.viewPermissionsView),
    url(r'^notification/$', views.notificationView, name='notification'),
    url(r'^activity/$', views.activityView, name='activity'),
    url(r'^get/notificationcount/', views.getNewNotificationCountJsonView),
    url(r'^get/notification/', views.getNotificationView),
    url(r'^get/activity/', views.getActivityView),
]

urlpatterns += [
    url(
        r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"
    ),
    url(
        r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'
    ),
    url(
        r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/user/password/done/'}
    ),
    url(
        r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'
    ),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
