import pytest
import sys

from pymysql.cursors import DictCursor

sys.path.append('..')
from app import create_app
from scripts.create_db import create_database

from db import get_db
from mail import mail


TEST_DB_NAME="test"
TEST_CONFIG={
    'TESTING': True,
    'MAIL_DEFAULT_SENDER': 'no-reply@wikispeedruns.com',
    'DATABASE': TEST_DB_NAME,
    # Same as in .github/workflows/build.yml
    'MYSQL_USER': 'testuser',
    'MYSQL_PASSWORD': 'testpassword',
}


@pytest.fixture(scope="session")
def test_db():
    create_database(TEST_DB_NAME, recreate=True, test_config=TEST_CONFIG)


@pytest.fixture(scope="session")
def app(test_db):
    yield create_app(test_config=TEST_CONFIG)


@pytest.fixture()
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
def user_with_outbox(client, mail, cursor):
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

    # Get user id and put it for users of this fixture
    get_id_query = "SELECT user_id FROM users WHERE username=%s"
    cursor.execute(get_id_query, user["username"])
    user["user_id"] = cursor.fetchone()["user_id"]

    yield user, outbox
    cursor.execute("DELETE FROM users WHERE username=%s", (user["username"],))

@pytest.fixture()
def user(user_with_outbox):
    user_info, _ = user_with_outbox
    yield user_info

@pytest.fixture()
def user2(client, mail, cursor):
    '''
    Adds a user for testing, with basic checks
    '''
    user2 = {
        "username" : "ahhhhhhh",
        "email" : "ahhhhhhh@gmail.com",
        "password" : "lmao"
    }

    client.post("/api/users/create/email", json=user2)

    # Get user id and put it for users of this fixture
    get_id_query = "SELECT user_id FROM users WHERE username=%s"
    cursor.execute(get_id_query, user2["username"])
    user2["user_id"] = cursor.fetchone()["user_id"]

    yield user2

    cursor.execute("DELETE FROM users WHERE username=%s", (user2["username"],))

@pytest.fixture()
def session(client, user):
    client.post("/api/users/login", json=user)
    yield user

@pytest.fixture()
def session2(client, user2):
    client.post("/api/users/login", json=user2)
    yield user2

@pytest.fixture()
def admin_session(client):
    with client.session_transaction() as session:
        session["user_id"] = 0
        session["username"] = "testadmin"
        session["admin"] = 1
