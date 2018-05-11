# -*- coding: utf-8 -*-
from django.utils.text import slugify
from djangotoolbox.admin import admin
from ikwen.accesscontrol.admin import MemberAdmin

from ikwen.accesscontrol.models import Member

from blog.models import Post, PostCategory, Comments


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count',)
    prepopulated_fields = {"slug": ("name",)}


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'language', 'publish', 'appear_on_main_page', 'member', 'pub_date')
    list_filter = ('member', 'publish', 'appear_on_main_page')
    search_fields = ('title',)
    readonly_fields = ('pub_date', 'member')
    # prepopulated_fields = {"slug": ("title",)}
    fields = ('category', 'title', 'summary', 'language', 'image', 'entry', 'order_of_appearance', 'publish', 'appear_on_main_page')

    def save_model(self, request, obj, form, change):
        obj.member = request.user
        obj.slug = slugify(obj.title)
        super(PostAdmin, self).save_model(request, obj, form, change)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('entry', 'pub_date','publish')
    search_fields = ('email',)
    list_filter = ('publish',)
    readonly_fields = ('post','entry','name', 'email','pub_date')
    fields = ('publish','post','entry','name', 'email','pub_date')


admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, CategoryAdmin)
admin.site.register(Comments, CommentAdmin)

# admin.site.unregister(Member)

admin.site.register(Member, MemberAdmin)