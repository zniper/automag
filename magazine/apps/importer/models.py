import os
import json
import re
import logging

from datetime import datetime

from django.db import models
from django.db.transaction import commit_on_success
from django.core.files import File
from django.conf import settings

from articles.models import Attachment
from apps.content.models import Article, SingleImage


INDEX_FILE = 'index.html'
META_FILE = 'index.json'
IMAGE_SLOT = '[{%d}]'
rg_image = re.compile(r'<img\s*.*?\/>')


class ImportProxy(models.Model):
    """ Marking the articles have been imported from local """
    local_path = models.CharField(max_length=256)
    url = models.CharField(max_length=256, blank=True, null=True)
    uid = models.CharField(max_length=128, blank=True, null=True)
    article = models.ForeignKey(Article, blank=True, null=True,
                                on_delete=models.SET_NULL)
    import_time = models.DateTimeField(default=datetime.now, blank=True,
                                       null=True)

    def open_file(self, path):
        """ Return file handler inside local path """
        return open(os.path.join(self.local_path, path), 'rb')

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

    def perform_import(self):
        """ Create new article base on local files """
        if not os.path.exists(self.local_path):
            return False
        with self.open_file(META_FILE) as metafile:
            self.meta = json.load(metafile)
        if self.meta.has_key('type') and self.meta.get('type').lower() == 'image':
            self.import_single_image()
        else:
            self.import_article()

        # Create proxy object
        with self.open_file(META_FILE) as metafile:
            self.meta = json.load(metafile)
            # Update import object
            self.uid = self.meta['hash']
            self.url = self.meta['url']
            self.save()

    @commit_on_success
    def import_single_image(self):
        """ Create new single image base on local files """
        simage = SingleImage(
            title=self.meta.get('title')[0],
            caption=self.meta.get('description')[0],
            author=self.meta.get('credit')[0],
            )
        imgfile = self.open_file(self.meta.get('extras')[0])
        simage.image = File(imgfile)
        simage.save()

    @commit_on_success
    def import_article(self):
        """ Create new article base on local files """
        # Load HTML content from local file
        index_file = self.open_file(INDEX_FILE)
        content = index_file.read()
        index_file.close()

        # Create new article
        article = Article(
            title=''.join(self.meta['title']) or 'Untitled',
            description=''.join(self.meta['description']) or '',
            keywords=''.join(self.meta['keywords']) or '',
            content=content,
            use_addthis_button=False,
            author_id=1,
            addthis_username='',
            )
        article.save()

        # Update import object
        self.article = article

        # Import attachments/images
        images_meta = self.meta.get('images', [])
        # Getting file list from directory may cause wrong order when importing
        #filelist = os.listdir(self.local_path)
        for imeta in images_meta:
            at_file = self.open_file(imeta[0])
            self.add_attachment(at_file, caption=imeta[1]['caption'])
            at_file.close()

        # update the article content
        article.content = self.make_image_slots(content)
        article.save()

    def __unicode__(self):
        desc = self.article.title if self.article else self.url
        return 'Import Proxy: %s' % desc
