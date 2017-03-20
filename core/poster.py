import logging
import os
import shutil
import urllib2
from HTMLParser import HTMLParser

from core.helpers import Url

logging = logging.getLogger(__name__)


class Poster():

    def __init__(self):
        self.poster_folder = u'static/images/posters/'

        if not os.path.exists(self.poster_folder):
            os.makedirs(self.poster_folder)

    def save_poster(self, imdbid, poster_url):
        ''' Saves poster locally
        :param imdbid: str imdb identification number (tt123456)
        :param poster_url: str url of poster image

        Saves poster as watcher/static/images/posters/[imdbid].jpg

        Does not return.
        '''

        logging.info(u'Grabbing poster for {}.'.format(imdbid))

        new_poster_path = u'{}{}.jpg'.format(self.poster_folder, imdbid)

        if os.path.exists(new_poster_path) is False:
            logging.info(u'Saving poster to {}'.format(new_poster_path))

            if poster_url == u'static/images/missing_poster.jpg':
                shutil.copy2(poster_url, new_poster_path)

            else:
                request = Url.request(poster_url)
                try:
                    result = Url.open(request)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    logging.error(u'Poster save_poster get', exc_info=True)

                try:
                    with open(new_poster_path, 'wb') as output:
                        output.write(result)
                    del result
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e: # noqa
                    logging.error(u'Unable to save poster to disk.', exc_info=True)

            logging.info(u'Poster saved to {}'.format(new_poster_path))
        else:
            logging.warning(u'{} already exists.'.format(new_poster_path))

    def remove_poster(self, imdbid):
        ''' Deletes poster from disk.
        :param imdbid: str imdb identification number (tt123456)

        Does not return.
        '''

        logging.info(u'Removing poster for {}'.format(imdbid))
        path = u'{}{}.jpg'.format(self.poster_folder, imdbid)
        if os.path.exists(path):
            os.remove(path)
        else:
            logging.warning(u'{} doesn\'t exist, cannot remove.'.format(path))
