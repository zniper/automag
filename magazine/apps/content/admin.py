from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django import forms
from articles.admin import ArticleAdmin as CoreArticleAdmin
from articles.forms import ArticleAdminForm

from apps.content.models import Article, Category


from tinymce.widgets import TinyMCE


class PageForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={'cols': 120, 'rows': 30}),
        }


class PageAdmin(FlatPageAdmin):
    form = PageForm


class ArticleForm(ArticleAdminForm):
    
    category = forms.ModelMultipleChoiceField(Category.objects.all())

    class Meta:
        model = Article
        widgets = {
            'content': TinyMCE(attrs={'cols': 120, 'rows': 30}),
        }


class ArticleAdmin(CoreArticleAdmin):
    form = ArticleForm
    fieldsets = (
        (None, {'fields': ('title', 'content', 'tags', 'auto_tag', 'markup', 'status')}),
        ('Metadata', {
            'fields': ('keywords', 'description', 'category'),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('followup_for', 'related_articles'),
            'classes': ('collapse',)
        }),
        ('Scheduling', {'fields': ('publish_date', 'expiration_date')}),
        ('AddThis Button Options', {
            'fields': ('use_addthis_button', 'addthis_use_author', 'addthis_username'),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('slug', 'is_active', 'login_required', 'sites'),
            'classes': ('collapse',)
        }),
    )


try:
    from articles.models import Article as CoreArticle
    admin.site.unregister(CoreArticle)
except:
    pass
admin.site.unregister(FlatPage)

admin.site.register(FlatPage, PageAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)
