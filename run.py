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


@celery.task
def classify(candidate, url=True, confidence=0.75):
    """
    Intake method to classify a provided candidate with an optional confidence
    :param candidate:
    :param url: True if the candidate is a url else candidate is treated as a DCU Image ID
    :param confidence: a minimum confidence value that must be between 0.75 and 1.0 (inclusive)
    Only matches greater than this param will be evaluated (unless this is 1.0, in which case,
    only exact matches are evaluated)
    :return: dictionary with at the following fields
    {
        "candidate": string,
        "type": string,
        "confidence": float,
        "target": string,
        "method": string,
        "meta": {
            // Additional data (implementation specific)
        }
    }
    """
    return _phash.classify(candidate, url, confidence)


@celery.task
def add_classification(imageid, abuse_type, target=''):
    """
        Hashes a given DCU image and adds it to the fingerprints collection
        :param imageid: Existing BSON image id
        :param abuse_type: Type of abuse associated with image
        :param target: Brand abuse is targeting if applicable
        :return Tuple: Boolean indicating success and a message
        Example:
        Invalid image id given
        (False, 'Unable to locate image xyz')
        Error trying to hash image
        (False, 'Unable to hash image xyz')
        A new document was inserted
        (True, '')
        A new document was not created. This can be for several reasons.
        Most likely a document with the same hash already exists
    """
    return _phash.add_classification(imageid, abuse_type, target)
