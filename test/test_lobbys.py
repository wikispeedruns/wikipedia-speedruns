from pydoc import cli
import pytest

import wikispeedruns

@pytest.fixture
def lobby(cursor, session):
    wikispeedruns.lobbys.create_lobby(session["user_id"])
    cursor.execute("DELETE FROM user_lobbys")
    cursor.execute("DELETE FROM lobbys")


def test_create_lobby(cursor, client, session):
    response = client.post("/api/lobbys", json={
        "name": "testlobby",
        "desc": "lobby for testing",
        "rules": {},
    })

    lobby_id = response.json["lobby_id"]

    # Assert that we inserted and are now deleting something
    assert 1 == cursor.execute("DELETE FROM user_lobbys WHERE lobby_id=%s", (lobby_id,))
    assert 1 == cursor.execute("DELETE FROM lobbys WHERE lobby_id=%s", (lobby_id,))

