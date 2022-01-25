import py
import pytest

from pymysql.cursors import DictCursor

test_user = {
    "username" : "echoingsins",
    "email" : "echoingsins@gmail.com", 
    "password" : "lmao"
}


@pytest.fixture()
def clean_up_users(test_db):
    yield
    with test_db.cursor(cursor=DictCursor) as cursor:
        cursor.execute("DELETE FROM users WHERE username=%s", (test_user["username"],))
        test_db.commit()


def test_create_user(client, clean_up_users):

    response = client.post("/api/users/create/email", json=test_user)
    assert response.status_code == 201
    
