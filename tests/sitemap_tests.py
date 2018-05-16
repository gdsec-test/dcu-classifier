import requests

from nose.tools import assert_equals, assert_false, assert_true, assert_is_none, assert_raises
from mock import patch, Mock
from datetime import timedelta
from requests.exceptions import RequestException
from service.parsers.parse_sitemap import SitemapParser


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, file_content, status_code):
            self.text = file_content
            self.status_code = status_code

        def json(self):
            return self.text

    SITEMAP_1_CONTENT = """
    <?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>http://example.com/sitemap_site.xml</loc>
        </sitemap>
        <sitemap>
            <loc>http://example.com/sitemap2.xml</loc>
        </sitemap>
    </sitemapindex>
    """

    SITEMAP_2_CONTENT = """
    <?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>http://example.com/sitemap_site.xml</loc>
        </sitemap>
        <sitemap>
            <loc>http://example.com/sitemap1.xml</loc>
        </sitemap>
    </sitemapindex>
    """

    if args[0] == 'http://example.com/sitemap1.xml':
        return MockResponse(SITEMAP_1_CONTENT, 200)
    elif args[0] == 'http://example.com/sitemap2.xml':
        return MockResponse(SITEMAP_2_CONTENT, 200)
    return MockResponse(None, 404)

class TestSitemapParser():
    DAYS_TO_GO_BACK = 1
    SITEMAP_URL_GOOD = 'http://example.com/sitemap1.xml'
    SITEMAP_URL_BAD = 'http://example.com/unknown_file.xml'
    EXPECTED_URL = 'http://www.example.com/catalog?item=12&desc=vacation_hawaii'

    def setUp(self):
        self._parser = SitemapParser(self.DAYS_TO_GO_BACK)
        self._todays_date = self._parser.TODAY.strftime(self._parser.DATE_FORMAT)
        self._two_days_ago = (self._parser.TODAY - timedelta(2)).strftime(self._parser.DATE_FORMAT)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_pass(self, mock_get):
        """
        Reads sitemap xml file from URL and passes
        :return:
        """
        url = None
        for url in self._parser.get_urls_from_web(self.SITEMAP_URL_GOOD):
            pass
        assert_is_none(url)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_fail_bad_path(self, mock_get):
        """
        Fails on a bad url
        :return:
        """
        assert_is_none(self._parser.get_urls_from_web(self.SITEMAP_URL_BAD))

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
