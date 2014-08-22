from logging import getLogger

from django.conf import settings
from django.contrib.sites.models import get_current_site

from open_facebook import OpenFacebook


logger = getLogger(__name__)


def build_url(path):
    """ Returns the complete (usable) URL from path """
    spath = path.strip().lower()
    if spath.find('http://') == 0 or spath.find('https://') == 0:
        return path
    else:
        domain = get_current_site(None).domain
        return ''.join(['http://', domain, path.strip()])


def write_facebook_status(message, link, picture=''):
    """ Post a link and message to Facebook page or timeline """
    link = build_url(link)
    if picture:
        picture = build_url(picture)
    message += ' ('+link+')'
    try:
        fb = OpenFacebook(settings.FACEBOOK_ACCESS_TOKEN)
        fb.set('me/feed', message=message, url=link, picture=picture)
    except:
        logger.error('Error when posting to Facebook page')
