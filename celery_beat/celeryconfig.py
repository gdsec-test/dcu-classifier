import os
from urllib.parse import quote


class CeleryConfig:
    broker_transport = 'pyamqp'
    broker_use_ssl = True
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    imports = 'run'
    worker_hijack_root_logger = False
    task_acks_late = True
    worker_prefetch_multiplier = 1
    worker_send_task_events = False

    def __init__(self, app_settings):
        self.BROKER_PASS = quote(os.getenv('BROKER_PASS', 'password'))
        self.broker_url = 'amqp://02d1081iywc7A:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'

        self.result_backend = app_settings.DBURL
        self.mongodb_backend_settings = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
