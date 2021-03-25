import logging.config
import os

import requests
import yaml
from celery import Celery, Task
from celery.utils.log import get_task_logger
from requests.exceptions import RequestException

from celeryconfig import CeleryConfig
from service.classifiers.ml_api import MLAPI
from service.parsers.parse_sitemap import SitemapParser
from settings import config_by_name

env = os.getenv('sysenv', 'dev')
config = config_by_name[env]()

celery = Celery()
celery.config_from_object(CeleryConfig(config))
logger = get_task_logger('celery.tasks')

log_level = os.getenv('LOG_LEVEL', 'INFO')


def replace_dict(dict_to_replace):
    """
    Replace empty logging levels in logging.yaml with environment appropriate levels
    :param dict_to_replace: logging.yaml is read into a dict which is passed in
    :return:
    """
    for k, v in dict_to_replace.items():
        if type(v) is dict:
            replace_dict(dict_to_replace[k])
        else:
            if v == 'NOTSET':
                dict_to_replace[k] = log_level


# setup logging
path = os.getenv('LOG_CFG', 'logging.yaml')
if os.path.exists(path):
    with open(path, 'rt') as f:
        lconfig = yaml.safe_load(f.read())
    replace_dict(lconfig)
    logging.config.dictConfig(lconfig)
else:
    logging.basicConfig(level=logging.INFO)
logging.raiseExceptions = True

if not config.ML_API_CERT or not config.ML_API_KEY:
    message = 'Missing ML_API certificate or key'
    logger.fatal(message)
    raise ValueError(message)


class ClassifyTask(Task):
    """
    Base class for classification tasks
    """
    MIN_FRAUD_SCORE_TO_CREATE_TICKET = 0.95

    def __init__(self):
        self._ml_api = MLAPI(config)
        self._parser = SitemapParser(config.MAX_AGE)
        self._logger = logging.getLogger(__name__)
        self._default_fraud_score = config.DEFAULT_FRAUD_SCORE

    @property
    def ml_api(self):
        return self._ml_api

    def run(self, *args, **kwargs):
        pass

    def _scan_uri(self, uri):
        """
        Calls the ML API with a URI to obtain a fraud score
        :param uri: string representing a URI
        :return: None
        """
        fraud_score = self.ml_api.get_score(uri)
        self._logger.info('URI {} assigned fraud_score: {}'.format(uri, fraud_score))
        if fraud_score >= self.MIN_FRAUD_SCORE_TO_CREATE_TICKET:
            try:
                headers = {'Authorization': config.API_JWT}
                payload = {
                    'type': 'PHISHING',
                    'source': uri,
                    'metadata': {
                        'fraud_score': fraud_score
                    }
                }
                if env == 'dev':  # safeguard; headers contains sensitive info
                    self._logger.info('Sending POST to {} with payload {} and headers {}'.format(config.API_URL,
                                                                                                 payload,
                                                                                                 headers))
                result = requests.post(config.API_URL, json=payload, headers=headers)
                if env == 'dev':
                    self._logger.info('Result from POST: status_code {} text {} json {}'.format(result.status_code,
                                                                                                result.text,
                                                                                                result.json()))
            except Exception as e:
                self._logger.error('Error posting ticket for {}: {}'.format(uri, e))


@celery.task(bind=True, base=ClassifyTask, name='classify.request')
def classify(self, data):
    """
    Return the fraud score for the given uri
    :param self: object reference to ClassifyTask
    :param data: dict
    :return: dict outlining results of classification. Don't include fraud_score if -1
    """
    results_dict = {
        'candidate': data.get('uri'),
        'id': self.request.id
    }
    fraud_score = self.ml_api.get_score(data.get('uri'))
    if fraud_score > self._default_fraud_score:
        results_dict['confidence'] = fraud_score
    return results_dict


@celery.task(bind=True, base=ClassifyTask, name='scan.request')
def scan(self, data):
    """
    Scan the given uri, and if the fraud_score meets a threshold, it will submit a ticket to the Abuse API
    :param self: object reference to ClassifyTask
    :param data: dict
    :return: dict outlining details of the scan task
    """
    uri = data.get('uri')
    if data.get('sitemap'):
        try:
            """
            At this point in time we've decided to not enumerate all URLs in the sitemap and only examine the
            top level site. This serves as a small stop gap so we can address performance issues as well as more
            specifically target the intentional phishing that may be present in GoCentral. 31 Aug 2018.
            """
            uri = uri.replace('sitemap.xml', '')
            self._scan_uri(uri)
        except RequestException as e:
            logger.error('Error fetching sitemap for {}: {}'.format(uri, e))
    else:
        self._scan_uri(uri)
    return {
        'id': self.request.id,
        'uri': uri,
        'sitemap': data.get('sitemap', False)
    }


@celery.task(ignore_result=True)
def backend_cleanup():
    """
    Consumes the periodic task generated by Celery Beat in order to clean up expired metadata from results.
    This task runs daily at 4 AM UTC and is published to the generic celery queue.
    :return:
    """
    celery.backend.cleanup()
