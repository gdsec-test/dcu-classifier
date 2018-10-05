import os

from celery import Celery
from celery.utils.log import get_task_logger

from celeryconfig import CeleryConfig
from settings import config_by_name

config = config_by_name[os.getenv('sysenv', 'dev')]()

celery = Celery()
celery.config_from_object(CeleryConfig(config))
logger = get_task_logger('celery.tasks')
