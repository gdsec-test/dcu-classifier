import os
from urllib.parse import quote


class AppConfig(object):
    DB = 'test'
    DBURL = 'localhost'
    DB_USER = 'dbuser'
    DB_HOST = 'localhost'
    BROKER_PASS = quote(os.getenv('BROKER_PASS', 'password'))
    BROKER_URL = 'amqp://02d1081iywc7Av2:' + BROKER_PASS + '@rmq-dcu.int.dev-godaddy.com:5672/grandma'

    def __init__(self):
        self.DB_PASS = quote(os.getenv('DB_PASS', 'password'))
        self.DBURL = 'mongodb://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phishv2'
    BROKER_PASS = quote(os.getenv('BROKER_PASS', 'password'))
    BROKER_URL = 'amqp://02d1081iywc7Av2:' + BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'
    BROKER_PASS = quote(os.getenv('BROKER_PASS', 'password'))
    BROKER_URL = 'amqp://02d1081iywc7Av2:' + BROKER_PASS + '@rmq-dcu.int.godaddy.com:5672/grandma'

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = '10.36.156.188'
    DB_USER = 'devuser'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class TestingConfig(AppConfig):
    DBURL = 'mongodb://localhost/devphishstory'
    COLLECTION = 'test'


config_by_name = {'dev': DevelopmentAppConfig,
                  'prod': ProductionAppConfig,
                  'ote': OTEAppConfig,
                  'test': TestingConfig}
