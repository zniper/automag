from django import template
from django.conf import settings
import re


register = template.Library()
rg_images = re.compile('(?<=\[\{)\d+(?=\}\])')


@register.filter(name='insert_images')
def insert_article_images(value, article):

    def encode_img(img_id):
        return '[{%s}]' % str(img_id)

    def build_tags(url='', alt=''):
        if url:
            content = """
                <div class="article-image col-xs-12 col-sm-12 clearfix">
                  <a class="photoset" href="%(url)s" title="%(alt)s">
                    <img src="%(url)s" alt="%(alt)s">
                  </a>
                </div>""" % {'url':url, 'alt':alt}
        else:
            content = """<div class="article-image col-xs-12 col-sm-12 clearfix"><img src="/static/img/no-image.png"><div>"""
        return content

    imgs = rg_images.findall(value)
    attachments = article.attachments.all()
    content = value
    for pk in imgs:
        try:
            attc = attachments[int(pk)]
            url = attc.attachment.url
            caption = attc.caption
        except ValueError:
            url = caption = None

        content = content.replace(
            encode_img(pk),
            build_tags(url, caption)
            )

    return content
