import os
import urllib.parse

from kombu import Exchange, Queue


class CeleryConfig:
    BROKER_TRANSPORT = 'pyamqp'
    BROKER_USE_SSL = True
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_IMPORTS = 'run'
    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_SEND_EVENTS = False
    CELERY_TRACK_STARTED = True
    CELERYD_CONCURRENCY = 2
    CELERY_TASK_RESULT_EXPIRES = 86400  # One day in seconds

    @staticmethod
    def _getqueues(exchange):
        env = os.getenv('sysenv', 'dev')

        queues = ()
        queue_modifier = ''
        if env != 'prod':
            queue_modifier = env
        else:
            ''' If this is the prod environment, listen to celery queue to run db cleanup.
            This code should be temporary once we switch over to environment based vhosts. 6 Sept 2018.
            '''
            queues = (
                Queue('celery', Exchange('celery'), routing_key='celery'),)  # Listen to celery queue to run db cleanup

        if os.getenv('WORKER_MODE') == 'classify':
            queues += (
                Queue(queue_modifier + 'classify_tasks', exchange=Exchange(exchange, type='topic'),
                      routing_key='classify.request'),
            )
        else:
            queues += (
                Queue(queue_modifier + 'scan_tasks', exchange=Exchange(exchange, type='topic'),
                      routing_key='scan.request'),
            )

        return queues

    def __init__(self, app_settings):
        self.BROKER_PASS = urllib.parse.quote(os.getenv('BROKER_PASS', 'password'))
        self.BROKER_URL = 'amqp://02d1081iywc7A:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'
        self.CELERY_RESULT_BACKEND = app_settings.DBURL
        self.CELERY_MONGODB_BACKEND_SETTINGS = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
        self.CELERY_QUEUES = CeleryConfig._getqueues(app_settings.EXCHANGE)
