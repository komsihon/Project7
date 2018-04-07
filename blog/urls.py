# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from ikwen.flatpages.views import FlatPageView

from blog.views import PostsList, PostDetails, save_comment, Search, AdminHome, PostPerCategory, get_media, delete_photo

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^(?P<post_slug>[-\w]+)/$', PostDetails.as_view(), name='details'),
    url(r'^search$', Search.as_view(), name='search'),
    url(r'^category/(?P<category_slug>[-\w]+)/$', PostPerCategory.as_view(), name='post_per_category'),
    url(r'^yommax/$', AdminHome.as_view(), name='admin_home'),
    url(r'^$', PostsList.as_view(), name='home'),
    url(r'^save_comment$', save_comment, name='save_comment'),
    url(r'^get_media$', get_media, name='get_media'),
    url(r'^delete_photo$', delete_photo, name='delete_photo'),
)