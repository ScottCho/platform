import pytest
import os

from app import flask_app
from config import config
ENV = os.getenv('FLASK_CONFIG') or 'default'

@pytest.fixture
def app():
    flask_app.config.from_mapping(
        FLASK_ENV='development',
        MAIL_PASSWORD='JwnbKvR6bshSLWrG',
        MAIL_USERNAME='xxxx@.com',
        MAIL_PORT = 587, 
        MAIL_USE_TLS = True,
        MAIL_SERVER='smtp.exmail.qq.com',
        MAIL_DEFAULT_SENDER='Frog <xxxx@.com>'
    )
    yield flask_app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
