from datetime import datetime

from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.urlresolvers import reverse

from articles.models import Article as CoreArticle
from articles.models import Attachment

from utils import write_facebook_status


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
            while len(slug) > 50:
                slug = '-'.join(slug.split('-')[:-1])

            not_unique = Article.objects.all()
            if hasattr(not_unique, 'using'):
                not_unique = not_unique.using(using)
            not_unique = not_unique.filter(publish_date__year=year, slug=slug)

            if len(not_unique) == 0:
                return slug

            slug = '%s%s' % (slug, counter)
            counter += 1


class SingleImage(models.Model):
    upload_to = lambda inst, fn: 'attach/%s/%s/%s' % (datetime.now().year, datetime.now().month, fn)
    title = models.CharField(max_length=256, default='')
    image = models.ImageField(upload_to=upload_to, max_length=256)
    caption = models.TextField(blank=True)
    author = models.CharField(max_length=128, blank=True)
    publish_date = models.DateTimeField(default=datetime.now())
    published = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        status = 'Published' if self.published else 'Draft'
        return 'Image: %s (%s)' % (self.title, status)




# MODEL SIGNAL RECEIVERS

@receiver(pre_delete, sender=Attachment)
def delete_mediafiles(sender, instance, **kwargs):
    instance.attachment.delete(False)


@receiver(post_save, sender=Article)
def publish_new_article(sender, instance, **kwargs):
    if instance.status.is_live:
        #message = '%s - %s' % (instance.title, instance.description)
        message = ''
        article_url = reverse('article-by-id', kwargs={'pk': instance.pk})
        write_facebook_status(message, article_url)
