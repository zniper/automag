from datetime import datetime

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings

from articles.models import Article as CoreArticle
from articles.models import Attachment


DEFAULT_DB = getattr(settings, 'ARTICLES_DEFAULT_DB', 'default')


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

    def get_unique_slug(self, slug, using=DEFAULT_DB):
        """Iterates until a unique slug is found"""

        # we need a publish date before we can do anything meaningful
        if type(self.publish_date) is not datetime:
            return slug

        orig_slug = slug
        year = self.publish_date.year
        counter = 1

        while True:
            if len(slug) > 50:
                slug = slug[:48]

            not_unique = Article.objects.all()
            if hasattr(not_unique, 'using'):
                not_unique = not_unique.using(using)
            not_unique = not_unique.filter(publish_date__year=year, slug=slug)

            if len(not_unique) == 0:
                return slug

            slug = '%s-%s' % (orig_slug, counter)
            counter += 1


class SingleImage(models.Model):
    upload_to = lambda inst, fn: 'attach/%s/%s/%s' % (datetime.now().year, datetime.now().month, fn)
    title = models.CharField(max_length=256, default='')
    image = models.ImageField(upload_to=upload_to)
    caption = models.TextField(blank=True)
    author = models.CharField(max_length=128, blank=True)
    publish_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return 'Image: '+self.title


@receiver(pre_delete, sender=Attachment)
def delete_mediafiles(sender, instance, **kwargs):
    instance.attachment.delete(False)
