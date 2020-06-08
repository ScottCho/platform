#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import os
from logging.handlers import SMTPHandler

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 设置默认的数据库信息
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SECRET_KEY = os.urandom(16)
    SECRET_KEY = 'dev'

    # 设置邮箱信息
    MAIL_DEBUG = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 设置每页显示的行数
    FLASKY_BASELINES_PER_PAGE = 20

    # 设置Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

    # 上传路径
    UPLOAD_FOLDER = '/data/frog/issue'

    @staticmethod
    def init_app(app):
        pass


# 开发环境


class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///'+os.path.join(basedir, 'platform_dev.sqlite')
    SQLALCHEMY_ECHO = True


# 测试环境
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'platform_test.sqlite')
    WTF_CSRF_ENABLED = False


# 生产环境
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'platform_dev.sqlite')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

mail_handler = SMTPHandler(
    (os.getenv('MAIL_SERVER'), os.getenv('MAIL_PORT')),
    os.getenv('MAIL_DEFAULT_SENDER'), [os.getenv('ADMIN_EMAIL')],
    'Frog Application Error',
    secure=(),
    credentials=(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD')))
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(
    logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))

# 将信息记录到日志文件
handler = logging.handlers.TimedRotatingFileHandler('/var/log/frog/app.log',
                                                    when='D',
                                                    interval=1,
                                                    backupCount=5,
                                                    encoding='UTF-8')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s -%(pathname)s - %(funcName)s - %(lineno)s - %(message)s'
)
handler.setFormatter(logging_format)