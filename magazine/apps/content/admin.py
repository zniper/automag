from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from articles.models import Article
from articles.admin import ArticleAdmin
from articles.forms import ArticleAdminForm

from tinymce.widgets import TinyMCE


class PageForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={'cols': 100, 'rows': 15}),
        }


class PageAdmin(FlatPageAdmin):
    form = PageForm


class ArticleForm(ArticleAdminForm):
    class Meta:
        model = Article
        widgets = {
            'content': TinyMCE(attrs={'cols': 100, 'rows': 15}),
        }


class ArticleAdmin(ArticleAdmin):
    form = ArticleForm


admin.site.unregister(FlatPage)
admin.site.unregister(Article)
admin.site.register(FlatPage, PageAdmin)
admin.site.register(Article, ArticleAdmin)
