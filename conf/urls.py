from django.conf.urls import patterns, include, url
from django.contrib import admin
from ikwen.flatpages.views import FlatPageView

from blog.views import PostsList, PostDetails, save_comment, Search, AdminHome, PostPerCategory

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^laakam/', include(admin.site.urls)),
    url(r'^ikwen/', include('ikwen.core.urls', namespace='ikwen')),
    url(r'^page/(?P<url>[-\w]+)/$', FlatPageView.as_view(), name='flatpage'),
    url(r'^', include('blog.urls', namespace='blog')),
)

