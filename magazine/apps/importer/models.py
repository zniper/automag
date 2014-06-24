import os
import json
import re

from datetime import datetime

from django.db import models
from django.db.transaction import commit_on_success
from django.core.files import File
from django.conf import settings

from articles.models import Attachment
from apps.content.models import Article


INDEX_FILE = 'index.html'
META_FILE = 'index.json'
IMAGE_SLOT = '[{%d}]'
rg_image = re.compile(r'<img\s*.*?\/>')


class ImportProxy(models.Model):
    """ Marking the articles have been imported from local """
    local_path = models.CharField(max_length=256)
    url = models.CharField(max_length=256, blank=True, null=True)
    uid = models.CharField(max_length=128, blank=True, null=True)
    article = models.ForeignKey(Article, blank=True, null=True)
    import_time = models.DateTimeField(default=datetime.now, blank=True,
                                       null=True)

    def open_file(self, path):
        """ Return file handler inside local path """
        return open(os.path.join(self.local_path, path), 'r')

    def add_attachment(self, attach_file, caption=''):
        """ Add attach_file to the article """
        file_name = os.path.basename(attach_file.name)
        attach = Attachment(article=self.article)
        attach.attachment = File(attach_file)
        attach.attachment.name = file_name
        if len(caption) > 255:
            caption = caption[:caption[:250].rfind(' ')] + '...'
        attach.caption = caption
        attach.save()
        return attach.attachment.name

    def make_image_slots(self, content):
        """ Convert <img> tags to [{num}] """
        count = 0
        for found in rg_image.findall(content):
            content = content.replace(found, IMAGE_SLOT % count)
            count += 1
        return content

    @commit_on_success
    def perform_import(self):
        """ Create new article base on local files """
        if not os.path.exists(self.local_path):
            return False

        # Load HTML content from local file
        index_file = self.open_file(INDEX_FILE)
        content = index_file.read()
        index_file.close()

        # Load metadata and create new article
        with self.open_file(META_FILE) as metafile:
            meta = json.load(metafile)
            article = Article(
                title=''.join(meta['title']) or 'Untitled',
                description=''.join(meta['description']) or '',
                keywords=''.join(meta['keywords']) or '',
                content=content,
                use_addthis_button=False,
                author_id=1,
                addthis_username='',
                )
            article.save()

            # Update import object
            self.article = article
            self.uid = meta['hash']
            self.url = meta['url']
            self.save()

        # Import attachments/images
        filelist = os.listdir(self.local_path)
        filelist.remove(INDEX_FILE)
        filelist.remove(META_FILE)
        captions = meta.get('images', {})
        for fname in filelist:
            at_file = self.open_file(fname)
            self.add_attachment(at_file, caption=captions.get(fname, ''))
            at_file.close()

        # update the article content
        article.content = self.make_image_slots(content)
        article.save()

    def __unicode__(self):
        return 'Import Proxy: %s' % self.article.title
