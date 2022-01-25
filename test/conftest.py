import pytest
import sys

sys.path.append('..')
from app import create_app

from db import get_db
from mail import mail


@pytest.fixture
def app():
    yield create_app({
        'TESTING': True, 
        'DATABASE': 'test', 
        'MAIL_DEFAULT_SENDER': 'no-reply@wikispeedruns.com'
    })


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

    # TODO cleanup?


@pytest.fixture
def test_mail():
    yield mail

@pytest.fixture
def test_db(app):
    with app.app_context():
        yield get_db()