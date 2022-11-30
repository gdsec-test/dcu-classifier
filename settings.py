import os
from urllib.parse import quote

TEST = 'test'


class AppConfig(object):
    DBURL = 'localhost'
    DB = TEST
    DB_PORT = 27017
    DB_USER = 'dbuser'
    DB_HOST = 'localhost'
    MAX_AGE = 1  # Maximum number of days old a URL can be for sitemap extraction

    API_TOKEN = os.getenv('API_TOKEN', 'token')
    API_CREATE_URL = os.getenv('ABUSE_API_CREATE_URL', 'http://abuse-api:5000/v1/abuse/tickets')

    URSULA_API_URL = os.getenv('URSULA_API_URL', 'http://localhost:8080/ursula/v1')
    URSULA_API_KEY = os.getenv('URSULA_API_KEY', 'api-key')
    URSULA_API_ENABLED = os.getenv('URSULA_API_ENABLED', 'False') == 'True'
    SSO_URL = 'https://sso.dev-gdcorp.tools'
    SSO_USER = os.getenv('SSO_USER', 'user')
    SSO_PASSWORD = os.getenv('SSO_PASSWORD', 'password')
    SCAN_SHOPPER_ID = 'empty'
    BROKER_URL = os.getenv('MULTIPLE_BROKERS')

    def __init__(self):
        self.WORKER_MODE = os.getenv('WORKER_MODE') or 'classify'  # should be either classify or scan


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phishv2'
    EXCHANGE = 'classifier'
    SSO_URL = 'https://sso.gdcorp.tools'
    SCAN_SHOPPER_ID = 'b3ec3417-96b8-4d86-be65-8b1a624fcb39'
    DB_PASS = quote(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else 'password'
    DBURL = 'mongodb://{}:{}@{}/?authSource={}'.format(DB_USER, DB_PASS, DB_HOST, DB)

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'
    EXCHANGE = 'oteclassifier'
    SSO_URL = 'https://sso.ote-gdcorp.tools'
    SCAN_SHOPPER_ID = ''
    DB_PASS = quote(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else 'password'
    DBURL = 'mongodb://{}:{}@{}/?authSource={}'.format(DB_USER, DB_PASS, DB_HOST, DB)

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = 'mongodb.cset.int.dev-gdcorp.tools'
    DB_USER = 'devuser'
    EXCHANGE = 'devclassifier'
    DB_PASS = quote(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else 'password'
    CLIENT_CERT = os.getenv("MONGO_CLIENT_CERT", '')
    DBURL = 'mongodb://{}:{}@{}/?authSource={}&readPreference=primary&directConnection=true&tls=true&tlsCertificateKeyFile={}'.format(DB_USER, DB_PASS, DB_HOST, DB, CLIENT_CERT)

    SCAN_SHOPPER_ID = 'ec3a04cf-49d3-42a8-8360-7e536ba5aef8'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class TestEnvironmentAppConfig(AppConfig):
    DB = 'testphishstory'
    DB_HOST = 'mongodb.cset.int.dev-gdcorp.tools'
    DB_USER = 'testuser'
    EXCHANGE = 'testclassifier'
    SCAN_SHOPPER_ID = ''
    DB_PASS = quote(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else 'password'
    CLIENT_CERT = os.getenv("MONGO_CLIENT_CERT", '')
    DBURL = 'mongodb://{}:{}@{}/?authSource={}&readPreference=primary&directConnection=true&tls=true&tlsCertificateKeyFile={}'.format(DB_USER, DB_PASS, DB_HOST, DB, CLIENT_CERT)

    def __init__(self):
        super(TestEnvironmentAppConfig, self).__init__()


class TestingConfig(AppConfig):
    DBURL = 'mongodb://localhost/devphishstory'

    URSULA_API_ENABLED = False
    URSULA_API_URL = 'http://localhost/ursula/v1'
    URSULA_API_KEY = 'api-key'
    SSO_URL = 'http://localhost/'
    SCAN_SHOPPER_ID = 'shopper'


config_by_name = {'dev': DevelopmentAppConfig,
                  'prod': ProductionAppConfig,
                  'ote': OTEAppConfig,
                  'test': TestEnvironmentAppConfig,
                  'unit-test': TestingConfig}
