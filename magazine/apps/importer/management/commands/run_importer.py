import os
import traceback
import logging

from django.conf import settings
from django.core.management.base import NoArgsCommand

from apps.importer.models import ImportProxy


logger = logging.getLogger('importer')


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """ Run import for all new directories """
        logger.info('')
        logger.info('Start loading content from: %s' % settings.AUTO_IMPORT_ROOT)
        content_dirs = get_content_dirs()
        new_dirs = filter_new_content(content_dirs.keys())
        logger.info('Found %d item(s), with %d new' %
                    (len(content_dirs), len(new_dirs)))
        for uid in new_dirs:
            import_content(content_dirs[uid])


def get_content_dirs():
    """ Return list of all paths of content directory """
    content_dirs = {}
    for node in os.walk(settings.AUTO_IMPORT_ROOT):
        if 'index.html' in node[2]:
            content_dirs[os.path.basename(node[0])] = node[0]
    return content_dirs


def filter_new_content(id_list):
    """ Returns only IDs of new content """
    new_ids = []
    for uid in id_list:
        if not ImportProxy.objects.filter(uid=uid).count():
            new_ids.append(uid)
    return new_ids


def import_content(dirpath):
    """ Just like the function name... """
    logger.info('Import %s' % dirpath)
    try:
        importer = ImportProxy(local_path=dirpath)
        importer.perform_import()
    except:
        logger.error('Error when importing %s' % dirpath)
        traceback.print_exc()
