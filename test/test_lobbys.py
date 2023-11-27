from pydoc import cli
import pytest

import wikispeedruns

@pytest.fixture
def lobby(cursor, user):
    lobby_id = wikispeedruns.lobbys.create_lobby(user["user_id"])

    cursor.execute(f"SELECT * FROM lobbys WHERE lobby_id={lobby_id}")
    yield cursor.fetchone()

    cursor.execute("DELETE FROM user_lobbys")
    cursor.execute("DELETE FROM lobbys")


def test_create_lobby(cursor, client, session):
    resp = client.post("/api/lobbys", json={
        "name": "testlobby",
        "desc": "lobby for testing",
        "rules": {},
    })

    lobby_id = resp.json["lobby_id"]

    # Assert that we inserted and are now deleting something
    assert 1 == cursor.execute("DELETE FROM user_lobbys WHERE lobby_id=%s", (lobby_id,))
    assert 1 == cursor.execute("DELETE FROM lobbys WHERE lobby_id=%s", (lobby_id,))


def test_join_lobby_anonymous(client, lobby):
    # Join lobby
    lobby_id = lobby["lobby_id"]
    resp = client.post(f"/api/lobbys/{lobby_id}/join", json={
        "name": "anonymous",
        "passcode": lobby["passcode"],
    })
    assert resp.status_code == 200

    # Make sure session is there
    with client.session_transaction() as session:
        # session converts to string it seems?
        session["lobbys"][str(lobby_id)] == "anonymous"

    # Make sure we can get lobby
    resp = client.get(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 200
    assert resp.json["lobby_id"] == lobby_id


def test_join_lobby_user(client, cursor, session2, lobby):
    lobby_id = lobby["lobby_id"]

    # Join lobby
    resp = client.post(f"/api/lobbys/{lobby_id}/join", json={
        "passcode": lobby["passcode"]
    })
    assert resp.status_code == 200

    # check user shows up in table
    query = "SELECT owner FROM user_lobbys WHERE user_id=%s AND lobby_id=%s"
    cursor.execute(query, (session2["user_id"], lobby_id))
    res = cursor.fetchone()
    assert res is not None and res["owner"] == False

    # Check we have new permissions
    resp = client.get(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 200
    assert resp.json["lobby_id"] == lobby_id


def test_permissions_anonymous(client, lobby):
    lobby_id = lobby["lobby_id"]

    resp = client.get(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 401

    resp = client.get(f"/api/lobbys/{lobby_id}/prompts")
    assert resp.status_code == 401


# small note, order of session and lobby matter, else this attempts to delete
# user without deleting from user_lobby
def test_permissions_user(client, session2, lobby):
    lobby_id = lobby["lobby_id"]

    resp = client.get(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 401

    resp = client.get(f"/api/lobbys/{lobby_id}/prompts")
    assert resp.status_code == 401

    # Join lobby as non owner, make sure prompt endpoints don't work
    resp = client.post(f"/api/lobbys/{lobby_id}/join", json={
        "passcode": lobby["passcode"]
    })

    resp = client.post(f"api/lobbys/{lobby_id}/prompts", json={
        "start": "test",
        "end": "test",
        "language": "en"
    })
    assert resp.status_code == 401
