from collections import namedtuple
from unittest import TestCase

import requests
from mock import patch
from selenium import webdriver

from service.utils.urihelper import URIHelper

HTML = 'Some HTML'


class MockUrllib3:
    def __init__(self, _source=''):
        self.data = str.encode(_source)


class MockPageSource:
    def __init__(self, _page_source_return_val):
        self._return_val = _page_source_return_val

    def encode(self, _, __):
        return self._return_val


class MockPhantom:
    def __init__(self, page_source_return_val):
        self.page_source = MockPageSource(page_source_return_val)

    def set_page_load_timeout(self, _):
        pass

    def get(self, _):
        pass

    def close(self):
        pass

    def quit(self):
        pass


class TestURIHelper(TestCase):
    URI = 'http://some.uri'

    def setUp(self):
        self._urihelper = URIHelper()
        self.test_url = 'http://someurlthatscool.com'

    @patch.object(requests.Session, 'request')
    def test_resolves_403(self, mocked_method):
        status = dict(status_code=403, status_message='FORBIDDEN')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertTrue(self._urihelper.resolves(self.test_url))

    @patch.object(requests.Session, 'request')
    def test_resolves_406(self, mocked_method):
        status = dict(status_code=406, status_message='UNACCEPTABLE')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertTrue(self._urihelper.resolves(self.test_url))

    @patch.object(requests.Session, 'request')
    def test_resolves_200(self, mocked_method):
        status = dict(status_code=200, status_message='SUCCESS')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertTrue(self._urihelper.resolves(self.test_url))

    @patch.object(requests.Session, 'request')
    def test_resolves_301(self, mocked_method):
        status = dict(status_code=301, status_message='MOVED')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertTrue(self._urihelper.resolves(self.test_url))

    @patch.object(requests.Session, 'request')
    def test_resolves_100(self, mocked_method):
        status = dict(status_code=100, status_message='CONTINUE')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertTrue(self._urihelper.resolves(self.test_url))

    @patch.object(requests.Session, 'request')
    def test_resolves_500(self, mocked_method):
        status = dict(status_code=500, status_message='FAIL')
        mocked_method.return_value = namedtuple('struct', list(status.keys()))(**status)
        self.assertFalse(self._urihelper.resolves(self.test_url))

    @patch.object(webdriver, 'PhantomJS', return_value=MockPhantom(None))
    def test_get_site_data_no_sourcecode(self, mock_phantom):
        self.assertIsNone(self._urihelper.get_site_data(self.URI))
        mock_phantom.assert_called()

    @patch.object(webdriver, 'PhantomJS', return_value=MockPhantom(HTML))
    def test_get_site_data_valid_sourcecode(self, mock_phantom):
        self.assertEqual(self._urihelper.get_site_data(self.URI), HTML)
        mock_phantom.assert_called()
