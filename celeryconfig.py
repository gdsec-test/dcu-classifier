import os

from celery import Celery
from kombu import Exchange, Queue

from settings import AppConfig, config_by_name

env = os.getenv('sysenv', 'dev')
config = config_by_name[env]()


class CeleryConfig:
    broker_transport = 'pyamqp'
    broker_use_ssl = not os.getenv('DISABLESSL', False)  # True unless local docker-compose testing
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json', 'pickle']
    imports = 'run'
    worker_hijack_root_logger = False
    task_acks_late = True
    worker_prefetch_multiplier = 1
    worker_send_task_events = False
    task_track_started = True
    worker_concurrency = 2
    result_expires = 86400  # One day in seconds
    WORKER_ENABLE_REMOTE_CONTROL = True

    @staticmethod
    def _get_queues(app_settings):
        env = os.getenv('sysenv', 'dev')

        queues = ()
        queue_modifier = ''
        if env != 'prod':
            queue_modifier = env
        else:
            ''' If this is the prod environment, listen to celery queue to run db cleanup.
            This code should be temporary once we switch over to environment based vhosts. 6 Sept 2018.
            '''
            # Listen to celery queue to run db cleanup. Force this to stay on a classic queue for backwards
            # compatibility.
            queues = (Queue('celery', exchange=Exchange('celery'), routing_key='celery', queue_arguments={'x-queue-type': 'classic'}),)
        if os.getenv('WORKER_MODE') == 'classify':
            queues += (
                Queue(queue_modifier + 'classify_tasks', exchange=Exchange(app_settings.EXCHANGE, type='topic'),
                      routing_key='classify.request', queue_arguments={'x-queue-type': 'quorum'}),
            )
        else:
            queues += (
                Queue(queue_modifier + 'scan_tasks', exchange=Exchange(app_settings.EXCHANGE, type='topic'),
                      routing_key='scan.request', queue_arguments={'x-queue-type': 'quorum'}),
            )

        return queues

    def __init__(self, app_settings: AppConfig):
        self.broker_url = app_settings.BROKER_URL

        self.result_backend = app_settings.DBURL
        self.mongodb_backend_settings = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
        self.task_queues = CeleryConfig._get_queues(app_settings)


app = Celery()
app.config_from_object(CeleryConfig(config))
