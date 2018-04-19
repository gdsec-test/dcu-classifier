import os
import yaml
import logging.config

from celery import Celery
from celery.utils.log import get_task_logger

from celeryconfig import CeleryConfig
from settings import config_by_name
from service.classifiers.phash import PHash

path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'logging.yml'
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

env = os.getenv('sysenv') or 'dev'
config = config_by_name[env]()
celery = Celery()
celery.config_from_object(CeleryConfig(config))
_logger = get_task_logger('celery.tasks')
_phash = PHash(config)


@celery.task(name='classify.request')
def classify(data):
    image_id = data.get('image_id')
    uri = data.get('uri')
    # Sanity check
    if (image_id is None and uri is None) or (image_id is not None and uri is not None):
        _logger.error('classify request received with too few/too many params!')
        return {
            'confidence': 0,
            'target': 'ERROR',
            'meta': 'This request was received with invalid parameters',
            'type': 'UNKNOWN'
        }
    if image_id:
        return _phash.classify(image_id, False, 0.75)
    return _phash.classify(uri, True, 0.75)
        

@celery.task(name='scan.request')
def scan(data):
    pass

@celery.task(name='fingerprint.request')
def add_classification(data): #imageid, abuse_type, target=''):
    return _phash.add_classification(data.get('image_id'), data.get('type'), data.get('target'))
