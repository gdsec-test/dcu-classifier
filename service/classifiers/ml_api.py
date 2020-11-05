import logging

import requests

from service.utils.urihelper import URIHelper


class MLAPI:

    """
    This class handles access to ML APIs: https://shopperml.godaddy.com/api-doc/
    """
    _header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    _urihelper = URIHelper()

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._url = settings.ML_API
        self._cert = (settings.ML_API_CERT, settings.ML_API_KEY)
        self._default_fraud_score = settings.DEFAULT_FRAUD_SCORE

    def get_score(self, source):
        """
        Returns Fraud probability for a Abuse Report
        :param source: source url of the reported phish
        :return: fraud_score
        """

        fraud_score = self._default_fraud_score

        try:
            html = self._urihelper.get_site_data(source)
            if not html:
                return
            payload = {'html': html}

            response = requests.post(self._url, json=payload, cert=self._cert, headers=self._header)
            if response.status_code == 200:
                fraud_score = response.json().get('fraud_score', self._default_fraud_score)
            else:
                self._logger.warning('Unable to retrieve Fraud Score from ML API for source url {}. API response: {}'.
                                     format(source, response.content))
        except Exception as e:
            self._logger.error('Exception while retrieving Fraud Score from ML API for source url {} with error: {}'.
                               format(source, e))
        finally:
            return fraud_score
