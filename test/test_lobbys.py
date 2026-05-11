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


# Admin / host role split (2.7) ---------------------------------------------
# `owner=1` means admin (one per lobby), `host=1` means co-host (many per
# lobby). Admin implicitly has host privileges.

def _login(client, user):
    resp = client.post("/api/users/login", json={
        "username": user["username"], "password": user["password"],
    })
    assert resp.status_code == 200


def _logout(client):
    client.post("/api/users/logout")


def _join_user(client, lobby):
    """Caller is responsible for being logged in. Joins as a registered user."""
    resp = client.post(f"/api/lobbys/{lobby['lobby_id']}/join", json={
        "passcode": lobby["passcode"],
    })
    assert resp.status_code == 200


def _user_role(cursor, lobby_id, user_id):
    """Returns ('admin' | 'host' | 'member' | None) for a given user in a lobby."""
    cursor.execute(
        "SELECT owner, host FROM user_lobbys WHERE lobby_id=%s AND user_id=%s",
        (lobby_id, user_id),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    if row["owner"]:
        return "admin"
    if row["host"]:
        return "host"
    return "member"


def test_promote_host_admin_only(client, cursor, user, user2, lobby):
    lobby_id = lobby["lobby_id"]

    # user2 joins as member
    _login(client, user2)
    _join_user(client, lobby)

    # user2 cannot promote themselves (they aren't admin)
    resp = client.patch(f"/api/lobbys/change_host/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 401
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "member"

    # Admin (user) promotes user2 successfully
    _logout(client)
    _login(client, user)
    resp = client.patch(f"/api/lobbys/change_host/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 200
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "host"


def test_host_cannot_promote_others(client, cursor, user, user2, lobby):
    # Promote user2 to host first.
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Now user2 (host, not admin) tries to promote someone — must 401.
    # We don't have a 3rd user; instead, just call the endpoint and confirm
    # the auth gate trips before the membership check.
    _logout(client)
    _login(client, user2)
    resp = client.patch(f"/api/lobbys/change_host/{lobby_id}", json={
        "target_user_id": 99999,
    })
    assert resp.status_code == 401


def test_demote_host_admin_only(client, cursor, user, user2, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Admin demotes successfully
    resp = client.patch(f"/api/lobbys/remove_host/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 200
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "member"


def test_admin_cannot_self_demote_via_remove_host(client, cursor, user, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user)
    resp = client.patch(f"/api/lobbys/remove_host/{lobby_id}", json={
        "target_user_id": user["user_id"],
    })
    assert resp.status_code == 400
    assert _user_role(cursor, lobby_id, user["user_id"]) == "admin"


def test_transfer_admin_swaps_roles(client, cursor, user, user2, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    # Promote user2 to host first (target must be a member of the lobby).
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Admin transfers
    resp = client.patch(f"/api/lobbys/transfer_admin/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 200
    assert _user_role(cursor, lobby_id, user["user_id"]) == "host"
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "admin"


def test_transfer_admin_host_blocked(client, cursor, user, user2, lobby):
    # Host (non-admin) attempting transfer must 401.
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    _logout(client)
    _login(client, user2)
    resp = client.patch(f"/api/lobbys/transfer_admin/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 401


def test_transfer_admin_to_plain_member_rejected(client, cursor, user, user2, lobby):
    # API requires target to already be a host (matches UI semantics — the
    # Transfer Admin button only appears on host rows).
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)  # user2 joins as plain member, not host
    _logout(client)
    _login(client, user)

    resp = client.patch(f"/api/lobbys/transfer_admin/{lobby_id}", json={
        "target_user_id": user2["user_id"],
    })
    assert resp.status_code == 400
    assert _user_role(cursor, lobby_id, user["user_id"]) == "admin"
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "member"


def test_transfer_admin_to_non_member_preserves_admin(cursor, db, user, lobby):
    # Regression for the zero-admin race: if transfer_admin is invoked on a
    # target with no user_lobbys row (simulating a TOCTOU between membership
    # check and SQL), the helper must NOT demote the existing admin.
    import wikispeedruns
    lobby_id = lobby["lobby_id"]

    # Caller is not a member of this lobby — simulates the racing scenario
    # where the row was deleted between API check and SQL.
    fake_user_id = 999999

    result = wikispeedruns.lobbys.transfer_admin(lobby_id, fake_user_id)
    assert result is False

    # Refresh from DB. user_lobbys row state must still have user as admin.
    db.commit()
    assert _user_role(cursor, lobby_id, user["user_id"]) == "admin"
    cursor.execute("SELECT COUNT(*) AS c FROM user_lobbys WHERE lobby_id=%s AND owner=1", (lobby_id,))
    assert cursor.fetchone()["c"] == 1


def test_delete_lobby_admin_only(client, cursor, user, user2, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Host cannot delete
    _logout(client)
    _login(client, user2)
    resp = client.delete(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 401

    # Admin can delete (this only hides; row still exists)
    _logout(client)
    _login(client, user)
    resp = client.delete(f"/api/lobbys/{lobby_id}")
    assert resp.status_code == 200


def test_host_can_add_prompts(client, cursor, user, user2, lobby):
    # Verify hosts retain prompt-add privilege (admin-or-host gate).
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    _logout(client)
    _login(client, user2)
    resp = client.post(f"/api/lobbys/{lobby_id}/prompts", json=PROMPT_PAYLOAD)
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 1


def test_host_can_delete_prompts(client, cursor, user, user2, lobby):
    # Hosts retain prompt-delete privilege (admin-or-host gate).
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Seed one prompt as admin.
    _seed_prompts(lobby_id, 1)
    cursor.execute("SELECT prompt_id FROM lobby_prompts WHERE lobby_id=%s", (lobby_id,))
    prompt_id = cursor.fetchone()["prompt_id"]

    _logout(client)
    _login(client, user2)
    resp = client.delete(f"/api/lobbys/{lobby_id}/prompts", json={"prompts": [prompt_id]})
    assert resp.status_code == 200
    assert _count_prompts(cursor, lobby_id) == 0


def test_admin_cannot_leave(client, cursor, user, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user)
    resp = client.delete(f"/api/lobbys/leave/{lobby_id}/")
    assert resp.status_code == 400
    assert _user_role(cursor, lobby_id, user["user_id"]) == "admin"


def test_host_can_leave(client, cursor, user, user2, lobby):
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    _logout(client)
    _login(client, user2)
    resp = client.delete(f"/api/lobbys/leave/{lobby_id}/")
    assert resp.status_code == 200
    assert _user_role(cursor, lobby_id, user2["user_id"]) is None


# Account-deletion handoff (2.7) --------------------------------------------

def test_delete_account_host_preserves_lobby(client, cursor, user, user2, lobby):
    # Co-host deleting their account must NOT delete the admin's lobby.
    # Regression for the cohost-cascade bug.
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    _logout(client)
    _login(client, user2)
    resp = client.delete("/api/users/delete_account")
    assert resp.status_code == 200

    # Lobby still exists, admin still admin.
    cursor.execute("SELECT COUNT(*) AS c FROM lobbys WHERE lobby_id=%s", (lobby_id,))
    assert cursor.fetchone()["c"] == 1
    assert _user_role(cursor, lobby_id, user["user_id"]) == "admin"
    assert _user_role(cursor, lobby_id, user2["user_id"]) is None


def test_delete_account_admin_with_host_transfers(client, cursor, user, user2, lobby):
    # Admin deletes account; co-host inherits admin; lobby survives.
    lobby_id = lobby["lobby_id"]
    _login(client, user2)
    _join_user(client, lobby)
    _logout(client)
    _login(client, user)
    client.patch(f"/api/lobbys/change_host/{lobby_id}", json={"target_user_id": user2["user_id"]})

    # Now delete admin's account.
    resp = client.delete("/api/users/delete_account")
    assert resp.status_code == 200

    cursor.execute("SELECT COUNT(*) AS c FROM lobbys WHERE lobby_id=%s", (lobby_id,))
    assert cursor.fetchone()["c"] == 1
    assert _user_role(cursor, lobby_id, user2["user_id"]) == "admin"


def test_delete_account_solo_admin_deletes_lobby(client, cursor, user, lobby):
    # Admin alone deletes account → lobby gets purged.
    lobby_id = lobby["lobby_id"]
    _login(client, user)
    resp = client.delete("/api/users/delete_account")
    assert resp.status_code == 200

    cursor.execute("SELECT COUNT(*) AS c FROM lobbys WHERE lobby_id=%s", (lobby_id,))
    assert cursor.fetchone()["c"] == 0
