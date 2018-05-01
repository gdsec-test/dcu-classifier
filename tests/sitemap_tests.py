from nose.tools import assert_equals, assert_false, assert_true

from datetime import timedelta
from service.parsers.parse_sitemap import SitemapParser


class TestSitemapParser():
    DAYS_TO_GO_BACK = 1
    SITEMAP_FILE_GOOD = 'files/sitemap.xml'
    SITEMAP_FILE_BAD = 'files/unknown_file.xml'
    SITEMAP_URI_BAD = 'http://example.com/unknown_file.xml'
    EXPECTED_URI = 'http://www.example.com/catalog?item=12&desc=vacation_hawaii'

    def setUp(self):
        self._parser = SitemapParser(self.DAYS_TO_GO_BACK)
        self._todays_date = self._parser.TODAY.strftime(self._parser.DATE_FORMAT)
        self._two_days_ago = (self._parser.TODAY - timedelta(2)).strftime(self._parser.DATE_FORMAT)

    def test_get_contents_file_pass(self):
        """
        Reads the good file, extracts the single good URL tag info
        :return:
        """
        uri_list = self._parser.get_contents_file(self.SITEMAP_FILE_GOOD)
        assert_equals(uri_list[0].get('uri'), self.EXPECTED_URI)
        assert_equals(uri_list[0].get('date'), self._todays_date)

    def test_get_contents_file_fail_bad_path(self):
        """
        Fails on a bad file path
        :return:
        """
        try:
            self._parser.get_contents_file(self.SITEMAP_FILE_BAD)
            assert False
        except IOError:
            assert True

    def test_get_contents_url_fail_bad_path(self):
        """
        Fails on a bad url
        :return:
        """
        try:
            self._parser.get_contents_url(self.SITEMAP_FILE_BAD)
            assert False
        except IOError:
            assert True

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
