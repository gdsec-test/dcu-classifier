import json
import logging
from enum import Enum
from typing import Tuple

import requests

from settings import AppConfig


class UrlClassification(Enum):
    CouldNotClassify = 'CouldNotClassify'
    NotPhishing = 'NotPhishing'
    Phishing = 'Phishing'
    Suspicious = 'Suspicious'


class UrsulaAPI:
    def __init__(self, settings: AppConfig):
        self._logger = logging.getLogger(__name__)
        self._url = f'{settings.URSULA_API_URL}/url-class'
        self._api_key = settings.URSULA_API_KEY

    def classify_url(self, url: str) -> Tuple[UrlClassification, float]:
        """
        Call into URSULA API and classify a URL. Throws an exception when an
        error is encountered.
        """

        payload = json.dumps({'url': url})
        headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'x-api-key': self._api_key}
        response = requests.post(self._url, headers=headers, data=payload)
        response.raise_for_status()
        if response.status_code == 214:
            return (UrlClassification.CouldNotClassify, 0.0)

        classification = response.json()
        return (UrlClassification(classification.get('classification')), classification.get('score'))
