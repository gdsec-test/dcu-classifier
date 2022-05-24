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

    # Machine Learning API
    ML_API = 'https://shopperml.godaddy.com/v1/predict/dcu_fraud_html/'
    DEFAULT_FRAUD_SCORE = -1.0

    API_TOKEN = os.getenv('API_TOKEN', 'token')
    API_CREATE_URL = os.getenv('ABUSE_API_CREATE_URL', 'http://abuse-api:5000/v1/abuse/tickets')

    URSULA_API_URL = os.getenv('URSULA_API_URL', 'http://localhost:8080/ursula/v1')
    URSULA_API_KEY = os.getenv('URSULA_API_KEY', 'api-key')
    URSULA_API_ENABLED = os.getenv('URSULA_API_ENABLED', 'False') == 'True'
    SSO_URL = 'https://sso.dev-godaddy.com'
    SSO_USER = os.getenv('SSO_USER', 'user')
    SSO_PASSWORD = os.getenv('SSO_PASSWORD', 'password')
    SCAN_SHOPPER_ID = 'empty'
    QUEUE_TYPE = os.getenv('QUEUE_TYPE')
    BROKER_URL = os.getenv('MULTIPLE_BROKERS') if QUEUE_TYPE == 'quorum' else os.getenv('SINGLE_BROKER')

    def __init__(self):
        self.DB_PASS = quote(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else 'password'
        self.DBURL = 'mongodb://{}:{}@{}/?authSource={}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)
        self.WORKER_MODE = os.getenv('WORKER_MODE') or 'classify'  # should be either classify or scan
        self.ML_API_CERT = os.getenv('ML_API_CERT')
        self.ML_API_KEY = os.getenv('ML_API_KEY')


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phishv2'
    EXCHANGE = 'classifier'
    SSO_URL = 'https://sso.godaddy.com'
    SCAN_SHOPPER_ID = '185469329'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'
    EXCHANGE = 'oteclassifier'
    SSO_URL = 'https://sso.ote-godaddy.com'
    SCAN_SHOPPER_ID = '1500031169'

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = '10.36.190.222'
    DB_USER = 'devuser'
    EXCHANGE = 'devclassifier'

    ML_API = 'https://shopperml.test-godaddy.com/v1/predict/dcu_fraud_html/'
    SCAN_SHOPPER_ID = '1440013'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class TestEnvironmentAppConfig(AppConfig):
    DB = 'testphishstory'
    DB_HOST = '10.36.190.222'
    DB_USER = 'testuser'
    EXCHANGE = 'testclassifier'
    ML_API = 'https://shopperml.test-godaddy.com/v1/predict/dcu_fraud_html/'
    SCAN_SHOPPER_ID = ''

    def __init__(self):
        super(TestEnvironmentAppConfig, self).__init__()


class TestingConfig(AppConfig):
    DBURL = 'mongodb://localhost/devphishstory'

    ML_API = TEST
    ML_API_CERT = TEST
    ML_API_KEY = TEST

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
