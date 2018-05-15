import logging
import os.path
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from requests.exceptions import RequestException


class SitemapParser:
    URL_TAG = 'url'
    SITEMAP_TAG = 'sitemap'
    TODAY = datetime.now()
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, days_to_go_back=1):
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
        return date_obj >= oldest_date

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
        changed_date = url_tag.lastmod.text.strip().split('T')[0]
        if self._date_within_threshold(changed_date):
            return changed_date

    def _get_uri_and_date(self, url_tag):
        """
        Extract the URI and last modified date from the tag
        :param url_tag:
        :return: tuple
        """
        return url_tag.loc.text.strip(), self._is_valid_date(url_tag)

    def _parse_sitemap_contents(self, parser):
        """
        Parse the sitemap xml file based on the parent tag as defined in self.URL_TAG
        :param parser:
        :return: returns a generator
        """
        urls = parser.find_all(self.URL_TAG)

        for url in urls:
            uri, change_date = self._get_uri_and_date(url)
            if change_date:
                yield uri

    def get_urls_from_filepath(self, filepath):
        """
        Assume you're receiving a filepath to a sitemap xml file.  Since we dont
        report back, we wont need to raise any Exceptions if we cant parse the
        filepath sitemap given or any of the urls in that file
        :param filepath:
        :return:
        """
        if not os.path.isfile(filepath):
            self._logger.error('Sitemap file not found {}'.format(filepath))
            return
        with open(filepath, 'r') as xmlfile:
            parser = bs(xmlfile, 'lxml')

        # Check to see if filepath is a sitemap-of-sitemaps.  If so, start
        #  recursive calls to this method
        sitemaps = parser.find_all(self.SITEMAP_TAG)
        if sitemaps:
            for sitemap in sitemaps:
                return self.get_urls_from_filepath(sitemap.loc.text.strip())
        return self._parse_sitemap_contents(parser)

    def get_urls_from_web(self, uri):
        """
        Assume you're receiving a url to a sitemap xml file
        :param uri:
        :return:
        """
        r = requests.get(uri)
        if r.status_code != requests.codes.ok:
            message = 'Bad status code "{}" while getting sitemap file {}'.format(r.status_code, uri)
            self._logger.error(message)
            raise RequestException(message)
        parser = bs(r.text, 'lxml')

        # Check to see if uri is a sitemap-of-sitemaps.  If so, start
        #  recursive calls to this method
        sitemaps = parser.find_all(self.SITEMAP_TAG)
        if sitemaps:
            for sitemap in sitemaps:
                return self.get_urls_from_web(sitemap.loc.text.strip())
        return self._parse_sitemap_contents(parser)
