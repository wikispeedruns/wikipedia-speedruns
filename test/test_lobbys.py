import json
from pydoc import cli
import pytest

import wikispeedruns

@pytest.fixture
def lobby(cursor, user):
    lobby_id = wikispeedruns.lobbys.create_lobby(user["user_id"])

    cursor.execute(f"SELECT * FROM lobbys WHERE lobby_id={lobby_id}")
    yield cursor.fetchone()

    cursor.execute("DELETE FROM lobby_prompts")
    cursor.execute("DELETE FROM user_lobbys")
    cursor.execute("DELETE FROM lobbys")


@pytest.fixture
def lobby_allow_anyone(cursor, user):
    lobby_id = wikispeedruns.lobbys.create_lobby(
        user["user_id"],
        rules=json.dumps({"allow_anyone_add_prompts": True}),
    )

    cursor.execute(f"SELECT * FROM lobbys WHERE lobby_id={lobby_id}")
    yield cursor.fetchone()

    cursor.execute("DELETE FROM lobby_prompts")
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


# Prompt submission permission matrix --------------------------------------
# Covers add_lobby_prompt under the allow_anyone_add_prompts rule, for
# owners, logged-in members, anonymous members, and non-members.

PROMPT_PAYLOAD = {"start": "Foo", "end": "Bar", "language": "en"}


def _join_as_anon(client, lobby, name="anon"):
    resp = client.post(f"/api/lobbys/{lobby['lobby_id']}/join", json={
        "name": name,
        "passcode": lobby["passcode"],
    })
    assert resp.status_code == 200


def _join_as_user(client, lobby):
    resp = client.post(f"/api/lobbys/{lobby['lobby_id']}/join", json={
        "passcode": lobby["passcode"],
    })
    assert resp.status_code == 200


def _count_prompts(cursor, lobby_id):
    cursor.execute("SELECT COUNT(*) AS c FROM lobby_prompts WHERE lobby_id=%s", (lobby_id,))
    return cursor.fetchone()["c"]


def test_add_prompt_owner_default(client, cursor, session, lobby):
    # Owner can always add prompts, regardless of allow_anyone_add_prompts.
    lobby_id = lobby["lobby_id"]
    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 1


def test_add_prompt_owner_allow_anyone(client, cursor, session, lobby_allow_anyone):
    lobby_id = lobby_allow_anyone["lobby_id"]
    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 1


def test_add_prompt_member_user_blocked_by_default(client, cursor, session2, lobby):
    # Logged-in non-owner member: should NOT be able to add when rule is off.
    lobby_id = lobby["lobby_id"]
    _join_as_user(client, lobby)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 401
    assert _count_prompts(cursor, lobby_id) == 0


def test_add_prompt_member_user_allowed_when_rule_on(client, cursor, session2, lobby_allow_anyone):
    # Logged-in non-owner member: should be allowed when rule is on.
    lobby_id = lobby_allow_anyone["lobby_id"]
    _join_as_user(client, lobby_allow_anyone)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 1


def test_add_prompt_anon_member_blocked_by_default(client, cursor, lobby):
    # Anonymous (passcode-joined) member: should NOT be able to add when rule is off.
    lobby_id = lobby["lobby_id"]
    _join_as_anon(client, lobby)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 401
    assert _count_prompts(cursor, lobby_id) == 0


def test_add_prompt_anon_member_allowed_when_rule_on(client, cursor, lobby_allow_anyone):
    # Anonymous (passcode-joined) member: allowed when rule is on. This is the
    # regression case from code review — previously @check_user 401'd them.
    lobby_id = lobby_allow_anyone["lobby_id"]
    _join_as_anon(client, lobby_allow_anyone)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 1


def test_add_prompt_non_member_anon_rejected(client, cursor, lobby_allow_anyone):
    # Anon who never joined the lobby is rejected even with rule on.
    lobby_id = lobby_allow_anyone["lobby_id"]
    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 401
    assert _count_prompts(cursor, lobby_id) == 0


def test_add_prompt_non_member_user_rejected(client, cursor, session2, lobby_allow_anyone):
    # Logged-in user who never joined is rejected even with rule on.
    lobby_id = lobby_allow_anyone["lobby_id"]
    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 401
    assert _count_prompts(cursor, lobby_id) == 0


from apis.lobbys_api import ANON_LOBBY_PROMPT_CAP


def _seed_prompts(lobby_id, n):
    for i in range(n):
        wikispeedruns.lobbys.add_lobby_prompt(lobby_id, f"Start_{i}", f"End_{i}", "en")


def test_add_prompt_capped_when_anon_enabled(client, cursor, session, lobby_allow_anyone):
    # When allow_anyone_add_prompts is on, the lobby is capped at
    # ANON_LOBBY_PROMPT_CAP total prompts. Cap applies to all submitters,
    # including the owner — owner deletes to free space.
    lobby_id = lobby_allow_anyone["lobby_id"]
    _seed_prompts(lobby_id, ANON_LOBBY_PROMPT_CAP)
    assert _count_prompts(cursor, lobby_id) == ANON_LOBBY_PROMPT_CAP

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 400
    assert _count_prompts(cursor, lobby_id) == ANON_LOBBY_PROMPT_CAP


def test_add_prompt_cap_blocks_anon_member(client, cursor, lobby_allow_anyone):
    lobby_id = lobby_allow_anyone["lobby_id"]
    _seed_prompts(lobby_id, ANON_LOBBY_PROMPT_CAP)

    _join_as_anon(client, lobby_allow_anyone)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 400
    assert _count_prompts(cursor, lobby_id) == ANON_LOBBY_PROMPT_CAP


def test_no_cap_when_anon_disabled(client, cursor, session, lobby):
    # Without allow_anyone_add_prompts, no cap — only the owner can add
    # anyway, so the abuse vector doesn't exist.
    lobby_id = lobby["lobby_id"]
    _seed_prompts(lobby_id, ANON_LOBBY_PROMPT_CAP)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == ANON_LOBBY_PROMPT_CAP + 1


def test_add_prompt_just_below_cap_succeeds(client, cursor, session, lobby_allow_anyone):
    lobby_id = lobby_allow_anyone["lobby_id"]
    _seed_prompts(lobby_id, ANON_LOBBY_PROMPT_CAP - 1)

    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == ANON_LOBBY_PROMPT_CAP
