from django.db import models

from articles.models import Article as CoreArticle


class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name


class Article(CoreArticle):
    """docstring for Article"""
    categories = models.ManyToManyField('Category')
