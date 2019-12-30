from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from math import *

# Create your views here.
import random, os
from blog.models import Post, Comments, PostCategory
from django.views.generic import TemplateView
from django.http import HttpResponse
import json
from django.utils import translation
from django.template.defaultfilters import slugify

from ikwen.core.models import Application
from ikwen.accesscontrol.models import Member
from ikwen.accesscontrol.backends import UMBRELLA

from conf import settings

POST_PER_PAGE = 5.00
MEDIA_DIR = settings.MEDIA_ROOT + 'tiny_mce/'
TINYMCE_MEDIA_URL = settings.MEDIA_URL + 'tiny_mce/'

ENGLISH = 'English'
FRENCH = 'Francais'

LANGUAGE_CHOICES = (
    (ENGLISH, 'English'),
    (FRENCH, 'Francais')
)

# user_langs = request.META.get('HTTP_ACCEPT_LANGUAGE', ['en-US', ])


class PostsList(TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super(PostsList, self).get_context_data(**kwargs)

        # lang = translation.get_language()
        lang = translation.get_language_from_request(self.request)
        if 'en' in lang:
            language = ENGLISH
        else:
            language = FRENCH
        post_list = list(Post.objects.select_related('member').filter(publish=True, appear_on_main_page=True, language=language).order_by('order_of_appearance'))

        # post_list = post_list.order_by('-pub_date')
        entry_list = []
        for suggestion in post_list:
            suggestion.member_on_umbrella = Member.objects.using(UMBRELLA).get(pk=suggestion.member.id)
            entry_list.append(suggestion)
        page_count = ceil(len(post_list) / POST_PER_PAGE)
        for entry in entry_list:
            comment_count = Comments.objects.filter(post=entry).count()
            entry.comment_count = comment_count
        context['items_paginated'] = get_paginated_view(self.request, entry_list, POST_PER_PAGE)
        context['entry_list'] = entry_list
        context['page_count'] = page_count
        context['lang'] = lang
        return context


class AdminHome(TemplateView):
    template_name = 'admin_home.html'


class Search(TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)
        radix = self.request.GET.get('radix')
        if radix == '':
            radix = "No-radix"

        entry_list = grab_items_by_radix(radix)
        page_count = ceil(len(entry_list)/ POST_PER_PAGE)
        context['items_paginated'] = get_paginated_view(self.request, entry_list, POST_PER_PAGE)
        context['pages'] = get_paginated_view(self.request, entry_list, POST_PER_PAGE)
        context['page_count'] = page_count
        context['entry_list'] = entry_list
        context['radix'] = radix
        return context


class PostPerCategory(TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):

        # lang = translation.get_language()
        lang = translation.get_language_from_request(self.request)
        if 'en' in lang:
            language = ENGLISH
        else:
            language = FRENCH
        context = super(PostPerCategory, self).get_context_data(**kwargs)
        category_slug = kwargs['category_slug']
        category = PostCategory.objects.get(slug=category_slug)
        radix = category.name + ' category'

        entry_list = Post.objects.filter(category=category, publish=True)
        context['items_paginated'] = get_paginated_view(self.request, entry_list, POST_PER_PAGE)
        context['pages'] = get_paginated_view(self.request, entry_list, POST_PER_PAGE)
        context['entry_list'] = entry_list
        context['radix'] = radix
        return context


class PostDetails(TemplateView):
    template_name = 'blog/post_details.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetails, self).get_context_data(**kwargs)
        slug = kwargs['post_slug']
        entry = get_object_or_404(Post, slug=slug)
        context['comments'] = Comments.objects.filter(post=entry, publish=True).order_by('id')
        context['post'] = entry
        actual_count = entry.visit_count
        entry.visit_count = actual_count + 1
        entry.save()
        return context


def get_paginated_view(rq, items, nos):
    items_paginated = True
    paginator = Paginator(items, nos)
    page = rq.GET.get('page')
    try:
        items_paginated = paginator.page(page)
    except PageNotAnInteger:
        items_paginated = paginator.page(1)
    except EmptyPage:
        items_paginated = paginator.page(paginator.num_pages)
    return items_paginated


def save_comment(request, *args, **kwargs):
    post_id = request.GET.get('post_id')
    email = request.GET.get('email')
    name = request.GET.get('name')
    entry = request.GET.get('comment')
    # post = get_object_or_404(Post, pk=post_id)
    post = Post.objects.get(pk=post_id)
    comment = Comments(post=post, name=name, email=email, entry=entry)
    comment.save()
    response = {
        'email': comment.email,
        'name': comment.name,
        'entry': comment.entry,
        'publ_date': comment.get_display_date()
    }
    return HttpResponse(
        json.dumps(response),
        'content-type: text/json',
        **kwargs
    )


def grab_items_by_radix(radix):
    items = []
    if radix is not None:
        radix.split(' ')
        posts_per_title = Post.objects.filter(title__icontains=radix, publish=True)
        posts_per_tags = Post.objects.filter(tags__icontains=radix, publish=True)
        posts_per_summary = Post.objects.filter(summary__icontains=radix, publish=True)
        posts_per_desc = Post.objects.filter(entry__icontains=radix, publish=True)
        posts = posts_per_title | posts_per_tags | posts_per_summary | posts_per_desc
        # items.extend([post for post in posts if post.image.name])
        items.extend([post for post in posts])
    return items
    # else:
    #     posts = Post.objects.filter(publish=True)


def get_media(request, *args, **kwargs):
    media_list = []
    for root, dirs, files in os.walk(MEDIA_DIR):
        for filename in files:
            if filename.lower():
                filename = TINYMCE_MEDIA_URL + filename
                media_list.append(os.path.join(filename))
    response = {
        'media_list': media_list,
    }
    return HttpResponse(
        json.dumps(response),
        'content-type: text/json',
        **kwargs
    )


def delete_photo(request, *args, **kwargs):
    filename = request.GET.get('filename')
    file_path = ''
    if filename:
        file_path = filename.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    try:
        os.remove(file_path)
        return HttpResponse(
            json.dumps({'success': True}),
            content_type='application/json'
        )
    except:
        response = "Error: %s file not found" % filename
        return HttpResponse(
            json.dumps({'error': response}),
            content_type='application/json'
        )


