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
    CELERY_TRACK_STARTED = True

    @staticmethod
    def _getqueues(exchange):
        env = os.getenv('sysenv')
        queue_modifier = ''
        if env != 'prod':
            queue_modifier = env
        if os.getenv('WORKER_MODE') == 'classify':
            return (
                Queue(queue_modifier+'fingerprint_tasks',   exchange=Exchange(exchange, type='topic'),
                        routing_key='fingerprint.request'),
                Queue(queue_modifier+'classify_tasks',   exchange=Exchange(exchange, type='topic'),
                        routing_key='classify.request'),
            )
        return (
            Queue(queue_modifier+'scan_tasks',   exchange=Exchange(exchange, type='topic'),
                    routing_key='scan.request'),
        )

    def __init__(self, app_settings):
        self.BROKER_PASS = os.getenv('BROKER_PASS', 'password')
        self.BROKER_PASS = urllib.quote(self.BROKER_PASS)
        self.BROKER_URL = 'amqp://02d1081iywc7A:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'
        self.CELERY_RESULT_BACKEND = app_settings.DBURL
        self.CELERY_MONGODB_BACKEND_SETTINGS = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
        self.CELERY_QUEUES = CeleryConfig._getqueues(app_settings.EXCHANGE)
