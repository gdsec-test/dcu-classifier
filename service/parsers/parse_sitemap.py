import logging
import os.path
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs


class SitemapParser:
    PARENT_TAG = 'url'
    TODAY = datetime.now()
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, days_to_go_back=1):
        self._parser = None
        self._days_to_go_back = days_to_go_back
        self._logger = logging.getLogger(__name__)

    def _date_within_threshold(self, date_string):
        """
        Compare the date extracted from the sitemap file to the oldest date we care about
        which is defined as a class member variable _days_to_go_back
        :param date_string:
        :return: boolean
        """
        date_obj = datetime.strptime(date_string, self.DATE_FORMAT)
        oldest_date = self.TODAY - timedelta(self._days_to_go_back)
        return date_obj > oldest_date

    def _is_valid_date(self, url_tag):
        """
        Checking for the presence of a lastmod date.  If none was found, assume the URI was modified
        today.  If a lastmod date was found, check to see if it is within the timeframe we care about
        :param url_tag:
        :return: string
        """
        if not url_tag.lastmod:
            return self.TODAY.strftime(self.DATE_FORMAT)

        # In the event the date is really a datetime, remove the time portion
        changed_date = url_tag.lastmod.text.split('T')[0]
        if self._date_within_threshold(changed_date):
            return changed_date

    def _get_uri_and_date(self, url_tag):
        """
        Extract the URI and last modified date from the tag
        :param url_tag:
        :return: tuple
        """
        return url_tag.loc.text, self._is_valid_date(url_tag)

    def _parse(self):
        """
        Parse the sitemap xml file based on the parent tag as defined in self.PARENT_TAG
        :return:
        """
        urls = self._parser.find_all(self.PARENT_TAG)
        uri_list_to_review = []

        for url in urls:
            (uri, change_date) = self._get_uri_and_date(url)
            if change_date:
                uri_list_to_review.append({'uri': uri, 'date': change_date})
        return uri_list_to_review

    def get_contents_file(self, filepath):
        """
        Assume you're receiving a filepath to a sitemap xml file
        :param filepath:
        :return:
        """
        if not os.path.isfile(filepath):
            message = 'Sitemap file not found {}'.format(filepath)
            self._logger.error(message)
            raise IOError(message)
        try:
            # BeautifulSoup takes an open file handle
            xml = open(filepath, 'r')
            self._parser = bs(xml, 'lxml')
        except Exception as e:
            self._logger.error('Error reading file {} : {}'.format(filepath, e.message))
            raise IOError(e.message)
        finally:
            xml.close()
        return self._parse()

    def get_contents_url(self, uri):
        """
        Assume you're receiving a url to a sitemap xml file
        :param uri:
        :return:
        """
        r = requests.get(uri)
        if r.status_code != requests.codes.ok:
            message = 'Bad status code "{}" while getting sitemap file {}'.format(r.status_code, uri)
            self._logger.error(message)
            raise IOError(message)
        self._parser = bs(r.text, 'lxml')
        return self._parse()
