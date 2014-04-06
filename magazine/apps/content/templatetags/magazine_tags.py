from django import template

from apps.content.models import Article


register = template.Library()


@register.assignment_tag
def get_latest_articles(limit=5):
    try:
        limit = int(limit)
    except ValueError:
        limit = 5
    articles = Article.objects.filter(status__is_live=True).order_by('-publish_date')[:limit]
    return articles
