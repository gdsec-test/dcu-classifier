from settings import AppConfig


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
    WORKER_ENABLE_REMOTE_CONTROL = True

    def __init__(self, app_settings: AppConfig):
        self.broker_url = app_settings.BROKER_URL

        self.result_backend = app_settings.DBURL
        self.mongodb_backend_settings = {
            'database': app_settings.DB,
            'taskmeta_collection': 'classifier-celery'
        }
