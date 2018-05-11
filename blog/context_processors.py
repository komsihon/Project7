import random
from ikwen_blog.blog.models import Post, PostCategory
from django.utils import translation

ENGLISH = 'English'
FRENCH = 'Francais'

LANGUAGE_CHOICES = (
    (ENGLISH, 'English'),
    (FRENCH, 'Francais')
)


def blog_base(request):
    lang = translation.get_language()
    if 'en' in lang:
        language = ENGLISH
    else:
        language = FRENCH
    rand = random.random()
    sugges = Post.objects.filter(publish=True, rand__lte=rand)[:5]
    suggestions = []
    for suggestion in sugges:
        if suggestion.image.name:
            suggestions.append(suggestion)
    categories = PostCategory.objects.filter(language=language)
    most_consulted = Post.objects.filter(publish=True).order_by('-visit_count')[:5]
    recents = Post.objects.filter(publish=True, language=language).order_by('created_on')[:5]
    recent_posts = []
    for suggestion in recents:
        if suggestion.image.name:
            recent_posts.append(suggestion)
    return {
                'categories': categories,
                'recent_posts': recent_posts,
                'suggestions': suggestions,
                'most_consulted':most_consulted ,
                'archives': recent_posts,

            }
