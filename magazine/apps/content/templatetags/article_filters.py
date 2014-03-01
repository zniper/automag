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
                <p class="image">
                  <a class="photoset" href="%(url)s" title="%(alt)s">
                    <img src="%(url)s" alt="%(alt)s">
                  </a>
                <p>""" % {'url':url, 'alt':alt}
        else:
            content = """<p class="image"><img src="/static/img/no-image.png"><p>"""
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
