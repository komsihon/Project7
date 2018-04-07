import random

from django.db import models
from datetime import datetime
# Create your models here.
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from ikwen.core.models import Application,Model, AbstractConfig
from ikwen.core.utils import to_dict
from ikwen.accesscontrol.models import Member


def to_display_date(a_datetime):
    now = datetime.now()
    if translation.get_language().lower().find('en') == 0:
        now_date = '%02d/%02d, %d' % (now.month, now.day, now.year)
        display_date = '%02d/%02d, %d %02d:%02d' % (
            a_datetime.month, a_datetime.day, a_datetime.year,
            a_datetime.hour, a_datetime.minute
        )
        display_date = display_date.replace(now_date, '').strip()
    else:
        now_date = '%02d/%02d/%d' % (now.day, now.month, now.year)
        display_date = '%02d/%02d/%d %02d:%02d' % (
            a_datetime.day, a_datetime.month, a_datetime.year,
            a_datetime.hour, a_datetime.minute
        )
        display_date = display_date.replace(now_date, '').strip()
    return display_date


class PostCategory(Model):
    name = models.CharField(max_length=240, blank=False, unique=True)
    slug = models.SlugField(max_length=240, blank=False, unique=True)
    media = models.ImageField(blank=True, null=True, upload_to='blog_img')

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "Categories"

    def _get_posts_count(self):
        return Post.objects.filter(publish=True, category=self).count()
    post_count = property(_get_posts_count)


class Post(Model):
    category = models.ForeignKey(PostCategory, blank=True, null=True,
                                 help_text=_("Category where the current post belongs to")
                                 )
    application = models.ForeignKey(Application, blank=True, null=True,
                                 help_text=_("Defined the application the blog is describing. I can be set to null")
                                 )
    title = models.CharField(max_length=240, blank=False, unique=True,
                             help_text=_("Main title of the post")
                             )
    summary = models.CharField(max_length=255, blank=True, null=True,
                             help_text=_("Few lines summary about the post; it will appears on the homepage"))
    slug = models.SlugField(max_length=240, blank=False, unique=True)
    media = models.ImageField(blank=True, null=True, upload_to='blog_img',
                             help_text=_("Photo describing the post; it appear on the top of the details page"))
    entry = models.TextField(blank=True, null=True,
                             help_text=_("Full description of your post"))
    pub_date = models.DateField(default=datetime.now)
    publish = models.BooleanField(default=False,
                             help_text=_("Allow the System to show this post or no"))
    member = models.ForeignKey(Member)
    tags = models.CharField(max_length=255, blank=True,
                             help_text=_("Few space separated keywords to process the post search easily"))
    likes = models.SmallIntegerField(default=0)
    visit_count = models.IntegerField(default=0,
                             help_text=_("Count of post read"))
    rand = models.FloatField(default=random.random, db_index=True, editable=False,
                             help_text=_("Specify the position the post should appear at the homepage"))
    order_of_appearance = models.SmallIntegerField(default=1000)
    appear_on_main_page = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.title

    def get_path(self):
        folders = '%s' % (self.slug)
        return '%s' % folders

    def get_uri(self):
        base_uri = getattr(settings, 'BASE_URI')
        return '%s%s' % (base_uri, self.get_path())

    def get_image_url(self):
        if self.media:
            return self.media.url


class Comments(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=45, blank=True)
    post = models.ForeignKey(Post)
    entry = models.TextField()
    pub_date = models.DateField(default=datetime.now)
    publish = models.BooleanField(default=False)

    def get_display_date(self):
        return to_display_date(self.pub_date)

    def to_dict(self):
        display_date = self.get_display_date()
        var = to_dict(self)
        var['publ_date'] = display_date
        del(var['pub_date'])