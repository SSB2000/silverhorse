import os
import json

with open('/etc/silverhorse_config.json') as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_USERNAME = 'mshubhambohra@gmail.com'
    MAIL_PASSWORD = 'shubhamBOHRA8755095967'
    WTF_CSRF_ENABLED = True
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
