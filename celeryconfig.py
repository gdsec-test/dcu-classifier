import os
from urllib.parse import quote

from kombu import Exchange, Queue


class CeleryConfig:
    broker_transport = 'pyamqp'
    broker_use_ssl = not os.getenv('DISABLESSL', False)  # True unless local docker-compose testing
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    imports = 'run'
    worker_hijack_root_logger = False
    task_acks_late = True
    worker_prefetch_multiplier = 1
    worker_send_task_events = False
    task_track_started = True
    worker_concurrency = 2
    result_expires = 86400  # One day in seconds

    @staticmethod
    def _get_queues(exchange):
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
        self.broker_url = os.getenv('BROKER_URL')  # For local docker-compose testing
        if not self.broker_url:
            self.BROKER_PASS = quote(os.getenv('BROKER_PASS', 'password'))
            self.broker_url = 'amqp://02d1081iywc7Av2:' + self.BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'
        self.result_backend = app_settings.DBURL
        self.mongodb_backend_settings = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
        self.task_queues = CeleryConfig._get_queues(app_settings.EXCHANGE)
