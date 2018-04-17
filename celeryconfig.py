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
        env = os.getenv('sysenv')
        if env == 'prod':
            env = ''
        if (os.getenv('WORKER_MODE') == 'classify'):
            self.CELERY_QUEUES = (
                    Queue(env+'fingerprint_tasks',   exchange=Exchange(app_settings.EXCHANGE, type='topic'),
                           routing_key='fingerprint.request'),
                    Queue(env+'classify_tasks',   exchange=Exchange(app_settings.EXCHANGE, type='topic'),
                           routing_key='classify.request'),
            )
        else:
            self.CELERY_QUEUES = (
                    Queue(env+'scan_tasks',   exchange=Exchange(app_settings.EXCHANGE, type='topic'),
                           routing_key='scan.request'),
            )
        self.CELERY_RESULT_BACKEND = app_settings.DBURL
        self.CELERY_MONGODB_BACKEND_SETTINGS = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
