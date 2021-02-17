import requests
from mock import patch
from nose.tools import assert_equal

from service.classifiers.ml_api import MLAPI
from service.utils.urihelper import URIHelper
from settings import TestingConfig


class MockResponseBad:
    """
    With no json() method, will cause exception to be thrown, returning the default fraud_score
    """
    status_code = 200


class MockResponseGood(MockResponseBad):
    """
    Constructor allows caller to specify class attributes.  Includes json() method
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def json(self):
        return self.__dict__


class TestMLAPI:
    URI = 'http://some.uri'
    HTML = 'Some HTML'
    DEFAULT_FRAUD_SCORE = -1.0
    VALID_FRAUD_SCORE = 0.789
    POST_METHOD = 'post'
    GET_SITE_DATE_METHOD = 'get_site_data'

    def __init__(self):
        config = TestingConfig()
        self._ml_api = MLAPI(config)

    @patch.object(requests, POST_METHOD, return_value=MockResponseBad())
    @patch.object(URIHelper, GET_SITE_DATE_METHOD, return_value=HTML)
    def test_get_score_exception_returns_default_fraud_score(self, mock_site_data, mock_post):
        assert_equal(self._ml_api.get_score(self.URI), self.DEFAULT_FRAUD_SCORE)

    @patch.object(requests, POST_METHOD, return_value=MockResponseGood(not_fraud_score='some value'))
    @patch.object(URIHelper, GET_SITE_DATE_METHOD, return_value=HTML)
    def test_get_score_200_post_no_fraud_score_returns_default_fraud_score(self, mock_site_data, mock_post):
        assert_equal(self._ml_api.get_score(self.URI), self.DEFAULT_FRAUD_SCORE)

    @patch.object(requests, POST_METHOD, return_value=MockResponseGood(fraud_score=VALID_FRAUD_SCORE))
    @patch.object(URIHelper, GET_SITE_DATE_METHOD, return_value=HTML)
    def test_get_score_200_post_returns_valid_fraud_score(self, mock_site_data, mock_post):
        assert_equal(self._ml_api.get_score(self.URI), self.VALID_FRAUD_SCORE)
