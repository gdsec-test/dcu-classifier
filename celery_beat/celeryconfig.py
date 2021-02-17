import os
import urllib


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

    def __init__(self, app_settings):
        self.BROKER_PASS = urllib.quote(os.getenv('BROKER_PASS', 'password'))
        self.BROKER_URL = 'amqp://02d1081iywc7A:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'

        self.CELERY_RESULT_BACKEND = app_settings.DBURL
        self.CELERY_MONGODB_BACKEND_SETTINGS = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
