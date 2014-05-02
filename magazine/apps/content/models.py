from datetime import datetime

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

    def get_latest_articles(self, number=1):
        qset = Article.objects.filter(categories=self, status__is_live=True)
        return qset.order_by('-publish_date')[:number]


class Article(CoreArticle):
    categories = models.ManyToManyField('Category')
    featured = models.BooleanField(default=False)


class SingleImage(models.Model):
    upload_to = lambda inst, fn: 'attach/%s/%s/%s' % (datetime.now().year, datetime.now().month, fn)
    title = models.CharField(max_length=256, default='')
    image = models.ImageField(upload_to=upload_to)
    caption = models.TextField(blank=True)
    author = models.CharField(max_length=128, blank=True)
    publish_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return 'Image: '+self.title
