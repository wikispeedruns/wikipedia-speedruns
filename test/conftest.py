import pytest
import sys

sys.path.append('..')
from app import create_app

from db import get_db
from mail import mail

from pymysql.cursors import DictCursor

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


@pytest.fixture(name="mail")
def mail_fixture():
    yield mail

@pytest.fixture(name="db")
def db_fixture(app):
    with app.app_context():
        yield get_db()


@pytest.fixture(name="cursor")
def db_cursor_fixture(db):
    with db.cursor(cursor=DictCursor) as cursor:
        yield cursor
        db.commit()

@pytest.fixture()
def user_base(client, mail, cursor):
    '''
    Adds a user for testing, with basic checks
    '''
    user = {
        "username" : "echoingsins",
        "email" : "echoingsins@gmail.com", 
        "password" : "lmao"
    }

    with mail.record_messages() as outbox:
        response = client.post("/api/users/create/email", json=user)

    yield user, outbox

    cursor.execute("DELETE FROM users WHERE username=%s", (user["username"],))

@pytest.fixture()
def user(user_base):
    user_info, _ = user_base
    yield user_info

@pytest.fixture()
def session(client, user):
    client.post("/api/users/login", json=user)
    yield user

@pytest.fixture()
def admin_session(client):
    with client.session_transaction() as session:
        session["user_id"] = 0
        session["username"] = "testadmin"
        session["admin"] = 1
