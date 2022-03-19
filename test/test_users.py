from flask import session

import datetime
import pytest
import re

import bcrypt
import hashlib

def test_create_user(cursor, user):
    cursor.execute("SELECT * FROM users WHERE username=%s", (user["username"],))
    result = cursor.fetchone()

    assert(result["join_date"] == datetime.date.today())


def test_create_existing_user(client, cursor, user):

    response = client.post("/api/users/create/email", json={
        "username" : user["username"],
        "email" : "test@test.com",
        "password" : "test"
    })
    assert response.status_code == 409

    response = client.post("/api/users/create/email", json={
        "username" : "test",
        "email" : user["email"],
        "password" : "test"
    })
    assert response.status_code == 409

    cursor.execute("SELECT COUNT(*) as num_users FROM users")
    assert cursor.fetchone()["num_users"] == 1


def test_old_hash_login(cursor, client):
    """
    Test our logic that converts our old buggy password hashes into new ones upon login
    """
    query = """
    INSERT INTO users (`username`, `hash`, `email`, `email_confirmed`, `is_old_hash`, `join_date`)
    VALUES ('test', %s, 'test@test.com', 0, 1, CURRENT_DATE())
    """
    password = "test"
    hash = bcrypt.hashpw(hashlib.sha256(password.encode()).digest(), bcrypt.gensalt())

    try:
        cursor.execute(query, (hash,))

        # abc is a password that used to generate null bytes
        response = client.post("/api/users/login", json={"username": "test", "password": "abc"})
        assert response.status_code == 401

        response =  client.post("/api/users/login", json={"username": "test", "password": password})
        assert response.status_code == 200

        cursor.execute("SELECT * FROM users WHERE username='test'")
        user = cursor.fetchone()
        assert user is not None and not user["is_old_hash"]

    finally:
        cursor.execute("DELETE FROM users")



def test_login_logout(client, user):
    def no_session():
        return all([field not in session for field in ["username", "user_id", "admin"]])

    def has_session():
        return "user_id" in session and session["username"] == user["username"] and not session["admin"]


    assert no_session()
    response = client.post("/api/users/login", json={"username": user["username"], "password": "wrongpassword"})
    assert response.status_code == 401
    assert no_session()

    response =  client.post("/api/users/login", json={"username": user["username"], "password": user["password"]})
    assert response.status_code == 200
    assert has_session()

    response = client.post("/api/users/logout")
    assert response.status_code == 200
    assert no_session()

    response = client.post("/api/users/login", json={"email": user["email"], "password": user["password"]})
    assert response.status_code == 200
    assert has_session()


def test_confirm_email(client, cursor, user_with_outbox):
    user, outbox = user_with_outbox

    assert len(outbox) == 1

    msg = outbox[0]
    assert msg.recipients == [user["email"]]

    # Make sure our templating is done correctly
    assert user["username"] in msg.html
    assert user["username"] in msg.body

    regex = r"confirm/([-_\.\w]+)"  # match alphanumeric characters and '_', '.', '-'
    token = re.search(regex, msg.html).groups()[0]

    # make sure token is the same in html and text
    assert token == re.search(regex, msg.body).groups()[0]

    # Try fake token
    assert client.post("/api/users/confirm_email", json={"token": "abc"}).status_code == 400

    # Use Token
    assert client.post("/api/users/confirm_email", json={"token": token}).status_code == 200

    # make sure it actually worked
    cursor.execute("SELECT email_confirmed FROM users WHERE username=%s", (user["username"],))
    assert cursor.fetchone()["email_confirmed"]


def test_change_password_bad(client, user):
    new_password = user["password"] + "2"

    # While not logged in, should return 401
    assert client.post("/api/users/change_password", json={
        "old_password": user["password"],
        "new_password": new_password
    }).status_code == 401


def test_change_password(client, user, session):
    new_password = user["password"] + "2"

    # Change for
    assert client.post("/api/users/change_password", json={
        "old_password": user["password"],
        "new_password": new_password
    }).status_code == 200

    # Check old password doesn't work
    assert client.post("/api/users/login", json={
        "email": user["email"],
        "password": user["password"]
    }).status_code == 401

    # And new password does
    assert client.post("/api/users/login", json={
        "email": user["email"],
        "password": new_password
    }).status_code == 200



def test_reset_password(client, mail, cursor, user, session):
    new_password = user["password"] + "2"

    # Send request to reset

    with mail.record_messages() as outbox:
        # Send request for our user
        assert client.post("/api/users/reset_password_request", json={"email": user["email"]}).status_code == 200

        # Try a non existent email for good measure, will still return 200 because we don't want ppls emails to leak
        assert client.post("/api/users/reset_password_request", json={"email": "notused@notexistent.com"}).status_code == 200

        # Check email is right
        assert len(outbox) == 1
        msg = outbox[0]
        assert msg.recipients == [user["email"]]
        assert user["username"] in msg.html and user["username"] in msg.body

        res = re.search( r"reset/([0-9]+)/([-_\.\w]+)", msg.html)
        id, token = res.groups()


        request = {"user_id": int(id), "password": new_password, "token": "test"}
        # try bad token, then good token
        assert client.post("/api/users/reset_password", json=request).status_code == 400

        # Try real token
        request["token"] = token
        resp = client.post("/api/users/reset_password", json=request)
        assert resp.status_code == 200

        # Try real token again to see if it expires properly
        client.post("/api/users/reset_password", json=request).status_code == 400

        # Check old password doesn't work
        assert client.post("/api/users/login", json={
            "email": user["email"],
            "password": user["password"]
        }).status_code == 401

        # And new password does
        assert client.post("/api/users/login", json={
            "email": user["email"],
            "password": new_password
        }).status_code == 200





