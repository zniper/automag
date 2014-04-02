import logging

from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django import forms

from tinymce.widgets import TinyMCE

from articles.admin import ArticleAdmin as CoreArticleAdmin
from articles.forms import ArticleAdminForm, tag
from articles import models as core_models

from models import Article, Category

log = logging.getLogger('articles.forms')


class PageForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={'cols': 120, 'rows': 30}),
        }


class PageAdmin(FlatPageAdmin):
    form = PageForm


class AttachmentInline(admin.TabularInline):
    model = core_models.Attachment
    extra = 5
    max_num = 25


class ArticleForm(ArticleAdminForm):
    categories = forms.ModelMultipleChoiceField(
        Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        )

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Article
        widgets = {
            'content': TinyMCE(attrs={'cols': 120, 'rows': 30}),
        }

    def clean_tags(self):
        """Turns the string of tags into a list"""
        tags = [tag(t.strip()) for t in self.cleaned_data['tags'].split()
            if len(t.strip())]
        log.debug('Tagging Article %s with: %s' %
            (self.cleaned_data.get('title', ''), tags))
        self.cleaned_data['tags'] = tags
        return self.cleaned_data['tags']


class ArticleAdmin(CoreArticleAdmin):
    form = ArticleForm
    fieldsets = (
        (None, {'fields': ('title', 'content', 'tags', 'auto_tag', 'markup', 'status')}),
        ('Metadata', {
            'fields': ('keywords', 'description', 'categories'),
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
    inlines = [AttachmentInline,]



def replace_model_admin(klass, new_klass):
    try:
        admin.site.unregister(klass)
    except:
        pass
    finally:
        admin.site.register(*new_klass)


replace_model_admin(core_models.Article, (Article, ArticleAdmin))
replace_model_admin(FlatPage, (FlatPage, PageAdmin))

admin.site.register(Category)

#try:
#    from articles.models import Article as CoreArticle
#    admin.site.unregister(CoreArticle)
#except:
#    pass
