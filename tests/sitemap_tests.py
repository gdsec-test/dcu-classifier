from nose.tools import assert_equals, assert_false, assert_true, assert_is_none, assert_raises

from datetime import timedelta
from requests.exceptions import RequestException
from service.parsers.parse_sitemap import SitemapParser


class TestSitemapParser():
    DAYS_TO_GO_BACK = 1
    SITEMAP_FILE_GOOD = 'files/sitemap.xml'
    SITEMAP_FILE_BAD = 'files/unknown_file.xml'
    SITEMAP_URL_GOOD = 'https://xmlsitemapgenerator.org/help/example-xml-sitemap.xml'
    SITEMAP_URL_BAD = 'http://example.com/unknown_file.xml'
    EXPECTED_URL = 'http://www.example.com/catalog?item=12&desc=vacation_hawaii'

    def setUp(self):
        self._parser = SitemapParser(self.DAYS_TO_GO_BACK)
        self._todays_date = self._parser.TODAY.strftime(self._parser.DATE_FORMAT)
        self._two_days_ago = (self._parser.TODAY - timedelta(2)).strftime(self._parser.DATE_FORMAT)

    def test_get_urls_from_filepath_pass(self):
        """
        Reads the good file, extracts the single good URL tag info
        :return:
        """
        for url in self._parser.get_urls_from_filepath(self.SITEMAP_FILE_GOOD):
            assert_equals(url, self.EXPECTED_URL)

    def test_get_urls_from_filepath_fail_bad_path(self):
        """
        Fails on a bad file path
        :return:
        """
        assert_raises(IOError, self._parser.get_urls_from_filepath, self.SITEMAP_FILE_BAD)

    def test_get_urls_from_web_pass(self):
        """
        Reads sitemap xml file from URL and passes
        :return:
        """
        url = None
        for url in self._parser.get_urls_from_web(self.SITEMAP_URL_GOOD):
            pass
        assert_is_none(url)

    def test_get_urls_from_web_fail_bad_path(self):
        """
        Fails on a bad url
        :return:
        """
        assert_raises(RequestException, self._parser.get_urls_from_web, self.SITEMAP_FILE_BAD)

    def test_date_within_threshold_pass(self):
        """
        Threshold is 1 day, and passes with today's date
        :return:
        """
        assert_true(self._parser._date_within_threshold(self._todays_date))

    def test_date_within_threshold_fail_out_of_range(self):
        """
        Threshold is 1 day, and fails with date from 2 days ago
        :return:
        """
        assert_false(self._parser._date_within_threshold(self._two_days_ago))
