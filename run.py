import os
import logging.config
import yaml
import requests

from celery import Celery, Task
from celeryconfig import CeleryConfig
from celery.utils.log import get_task_logger
from requests.exceptions import RequestException
from settings import config_by_name
from service.classifiers.phash import PHash
from service.parsers.parse_sitemap import SitemapParser

env = os.getenv('sysenv', 'dev')
config = config_by_name[env]()
celery = Celery()
celery.config_from_object(CeleryConfig(config))

path = 'logging.yml'
value = os.getenv('LOG_CFG', None)
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        lconfig = yaml.safe_load(f.read())
    logging.config.dictConfig(lconfig)
else:
    logging.basicConfig(level=logging.INFO)
logging.raiseExceptions = True
logger = get_task_logger(__name__)

class ClassifyTask(Task):
    '''
    Base class for classification tasks
    '''

    def __init__(self):
        self._phash = PHash(config)
        self._parser = SitemapParser(config.MAX_AGE)

    @property
    def phash(self):
        return self._phash

    def run(self, *args, **kwargs):
        pass

    def _scanuri(self, uri):
        results = self.phash.classify(uri, url=True, confidence=0.75)
        logger.debug('Scanned uri {} and got results: {}'.format(uri, results))
        if results.get('confidence', 0.0) >= 0.79:
            try:
                headers = {'Authorization': config.API_JWT}
                payload = {
                    'type': results.get('type'),
                    'source': uri,
                    'target': results.get('target', '')
                }
                if env == 'dev': #safeguard; headers contains sensitive info
                    logger.debug('Sending POST to {} with payload {} and headers {}'.format(config.API_URLL, payload, headers))
                result = requests.post(config.API_URL, json=payload, headers=headers)
                if env == 'dev':
                    logger.debug('Result from POST: status_code {} text {} json {}'.format(result.status_code, result.text, result.json()))
            except Exception as e:
                logger.error('Error posting ticket for {}: {}'.format(uri, e.message))


@celery.task(bind=True, base=ClassifyTask, name='classify.request')
def classify(self, data):
    '''
    Classify the given uri or image
    :param data:
    :return: dict outlining results of classification
    '''
    image_id = data.get('image_id')
    uri = data.get('uri')
    if image_id:
        results = self.phash.classify(image_id, url=False, confidence=0.75)
    else:
        results = self.phash.classify(uri, url=True, confidence=0.75)
    results['id'] = self.request.id
    return results


@celery.task(bind=True, base=ClassifyTask, name='scan.request')
def scan(self, data):
    '''
    Scan the given uri or image
    :param data:
    :return: dict outlining details of the scan task
    '''

    uri = data.get('uri')

    if data.get('sitemap'):
        try:
            for url in self._parser.get_urls_from_web(uri):
                self._scanuri(url)
        except RequestException as e:
            logger.error('Error fetching sitemap for {}: {}'.format(uri, e.message))
    else:
        self._scanuri(uri)
    return {
        'id': self.request.id,
        'uri': uri,
        'sitemap': data.get('sitemap', False)
    }

@celery.task(bind=True, base=ClassifyTask, name='fingerprint.request', ignore_result=True)
def add_classification(self, data):
    '''
    Fingerprint the given image for use in future classification requests
    :param data:
    :return:
    '''
    return self.phash.add_classification(data.get('image_id'), data.get('type'), data.get('target'))


