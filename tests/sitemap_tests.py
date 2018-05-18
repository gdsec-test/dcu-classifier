from nose.tools import assert_equals, assert_false, assert_true, assert_is_none
from mock import patch
from datetime import timedelta
from service.parsers.parse_sitemap import SitemapParser


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, file_content, status_code):
            self.text = file_content
            self.status_code = status_code

        def json(self):
            return self.text

    sitemap_1_content = """
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

    sitemap_2_content = """
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

    sitemap_3_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
       <url>
          <loc>http://www.example.com/</loc>
          <lastmod>2005-01-01</lastmod>
          <changefreq>monthly</changefreq>
          <priority>0.8</priority>
       </url>
       <url>
          <loc>http://www.example.com/good</loc>
          <changefreq>weekly</changefreq>
       </url>
       <url>
          <loc>http://www.example.com/catalog?item=12&amp;desc=vacation_hawaii</loc>
          <changefreq>weekly</changefreq>
       </url>
       <url>
          <loc>http://www.example.com/catalog?item=73&amp;desc=vacation_new_zealand</loc>
          <lastmod>2004-12-23</lastmod>
          <changefreq>weekly</changefreq>
       </url>
    </urlset>
    """

    sitemap_4_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>http://example.com/sitemap_site.xml</loc>
        </sitemap>
        <sitemap>
            <loc>http://example.com/sitemap5.xml</loc>
        </sitemap>
        <sitemap>
            <loc>http://example.com/sitemap3.xml</loc>
        </sitemap>
    </sitemapindex>
    """

    sitemap_5_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
       <url>
          <loc>http://www.example5.com/</loc>
          <lastmod>2005-01-01</lastmod>
          <changefreq>monthly</changefreq>
          <priority>0.8</priority>
       </url>
       <url>
          <loc>http://www.example5.com/good</loc>
          <changefreq>weekly</changefreq>
       </url>
       <url>
          <loc>http://www.example5.com/catalog?item=12&amp;desc=vacation_hawaii</loc>
          <changefreq>weekly</changefreq>
       </url>
       <url>
          <loc>http://www.example5.com/catalog?item=73&amp;desc=vacation_new_zealand</loc>
          <lastmod>2004-12-23</lastmod>
          <changefreq>weekly</changefreq>
       </url>
    </urlset>
    """

    if args[0] == 'http://example.com/sitemap1.xml':
        return MockResponse(sitemap_1_content, 200)
    elif args[0] == 'http://example.com/sitemap2.xml':
        return MockResponse(sitemap_2_content, 200)
    elif args[0] == 'http://example.com/sitemap3.xml':
        return MockResponse(sitemap_3_content, 200)
    elif args[0] == 'http://example.com/sitemap4.xml':
        return MockResponse(sitemap_4_content, 200)
    elif args[0] == 'http://example.com/sitemap5.xml':
        return MockResponse(sitemap_5_content, 200)
    return MockResponse(None, 404)


class TestSitemapParser():
    DAYS_TO_GO_BACK = 1
    SITEMAP_URL_GOOD = 'http://example.com/sitemap1.xml'
    SITEMAP_URL_BAD = 'http://example.com/unknown_file.xml'
    SITEMAP_URL_GOOD_3 = 'http://example.com/sitemap3.xml'
    SITEMAP_URL_GOOD_4 = 'http://example.com/sitemap4.xml'
    EXPECTED_URL = 'http://www.example.com/catalog?item=12&desc=vacation_hawaii'

    def setUp(self):
        self._parser = SitemapParser(self.DAYS_TO_GO_BACK)
        self._todays_date = self._parser.TODAY.strftime(self._parser.DATE_FORMAT)
        self._two_days_ago = (self._parser.TODAY - timedelta(2)).strftime(self._parser.DATE_FORMAT)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_sitemap_pass(self, mock_get):
        """
        Reads sitemap xml file from URL and passes
        :return:
        """
        count = 0
        for url in self._parser.get_urls_from_web(self.SITEMAP_URL_GOOD_3):
            count += 1
        assert_equals(url, self.EXPECTED_URL)
        assert_equals(count, 2)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_sitemap_of_sitemaps_pass(self, mock_get):
        """
        Reads sitemap xml file from URL and passes
        :return:
        """
        count = 0
        for url in self._parser.get_urls_from_web(self.SITEMAP_URL_GOOD_4):
            count += 1
        assert_equals(url, self.EXPECTED_URL)
        assert_equals(count, 4)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_fail_redundant_sitemap(self, mock_get):
        """
        Reads sitemap xml file from URL which contains a secondary sitemap xml
        file which points back to it.  Should avoid cyclical redundancy
        :return:
        """
        assert_equals(self._parser.get_urls_from_web(self.SITEMAP_URL_GOOD), [])

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_from_web_fail_bad_path(self, mock_get):
        """
        Fails on a bad url
        :return:
        """
        assert_equals(self._parser.get_urls_from_web(self.SITEMAP_URL_BAD), [])

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
