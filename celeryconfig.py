import os
import urllib

from kombu import Exchange, Queue


class CeleryConfig:
    BROKER_TRANSPORT = 'pyamqp'
    BROKER_USE_SSL = True
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']
    CELERY_IMPORTS = 'run'
    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_SEND_EVENTS = False

    def __init__(self, app_settings):
        self.BROKER_PASS = os.getenv('BROKER_PASS', 'password')
        self.BROKER_PASS = urllib.quote(self.BROKER_PASS)
        self.BROKER_URL = 'amqp://02d1081iywc7A:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'
        self.CELERY_QUEUES = (
            Queue(app_settings.INBOUND_QUEUE,
                  Exchange(app_settings.INBOUND_QUEUE, type="topic"),
                  routing_key=app_settings.WORKER_MODE + '.request'),
        )
        self.CELERY_DEFAULT_QUEUE = app_settings.INBOUND_QUEUE
        self.CELERY_RESULT_BACKEND = app_settings.DBURL
        self.CELERY_MONGODB_BACKEND_SETTINGS = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
