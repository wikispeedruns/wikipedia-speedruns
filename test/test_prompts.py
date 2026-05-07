import datetime
import enum
import pytest

from wikispeedruns import prompts

PROMPTS = [
    {
        "start" : "Johns Hopkins University",
        "end" : "Baltimore", 
    },
    {
        "start" : "A",
        "end" : "B", 
    },
]


@pytest.fixture()
def prompt_set(cursor):
    query = "INSERT INTO sprint_prompts (prompt_id, start, end) VALUES (%s, %s, %s);"
    ps = [(i, p["start"], p["end"]) for i, p in enumerate(PROMPTS)]
    cursor.executemany(query, ps)

    yield

    cursor.execute("DELETE FROM sprint_prompts")


@pytest.fixture()
def archive_search_prompt_set(cursor):
    now = datetime.datetime.now()
    active_start = now - datetime.timedelta(hours=1)
    active_end = now + datetime.timedelta(hours=1)
    expired_start = now - datetime.timedelta(days=2)
    expired_end = now - datetime.timedelta(days=1)

    query = """
    INSERT INTO sprint_prompts (start, end, active_start, active_end)
    VALUES (%s, %s, %s, %s);
    """
    cursor.executemany(query, [
        ("Visible Start Leak Probe", "Hidden End Needle", active_start, active_end),
        ("Expired Start Needle", "Expired End Needle", expired_start, expired_end),
    ])

    yield

    cursor.execute(
        "DELETE FROM sprint_prompts WHERE start IN (%s, %s)",
        ("Visible Start Leak Probe", "Expired Start Needle"),
    )


def test_create_prompt(client, cursor, admin_session):
    response = client.post("/api/sprints/", json=PROMPTS[0])
    assert response.status_code == 200
    
    cursor.execute("SELECT start, end FROM sprint_prompts")
    assert cursor.fetchone() == PROMPTS[0]
    cursor.execute("DELETE FROM sprint_prompts")



def test_create_no_admin(client, cursor):
    response = client.post("/api/sprints/", json=PROMPTS[0])
    assert response.status_code == 401
    
    cursor.execute("SELECT start, end FROM sprint_prompts")
    assert cursor.fetchone() is None



def test_delete(client, cursor, prompt_set, admin_session):
    # Try deleting id 1, which should be inserted
    id = 1
    response = client.delete(f"/api/sprints/{id}")
    assert response.status_code == 200
    cursor.execute("SELECT start, end FROM sprint_prompts WHERE prompt_id=%s", (id, ))
    assert cursor.fetchone() is None


def test_delete_nonexistent(client, cursor, prompt_set, admin_session):
    # Try deleting id 1, which should be inserted
    id = len(PROMPTS)
    response = client.delete(f"/api/sprints/{id}")
    assert response.status_code == 404


def test_delete_no_admin(client, cursor, prompt_set):
    id = 1
    response = client.delete(f"/api/sprints/{id}")
    assert response.status_code == 401
    cursor.execute("SELECT start, end FROM sprint_prompts WHERE prompt_id=%s", (id, ))
    assert cursor.fetchone() == PROMPTS[id]


def test_archive_search_does_not_match_active_end(cursor, archive_search_prompt_set):
    archive_prompts, num_prompts = prompts.get_archive_prompts("sprint", search="Hidden End Needle")

    assert num_prompts == 0
    assert archive_prompts == []


def test_archive_search_matches_active_start_without_revealing_end(cursor, archive_search_prompt_set):
    archive_prompts, num_prompts = prompts.get_archive_prompts("sprint", search="Visible Start Leak Probe")

    assert num_prompts == 1
    assert archive_prompts[0]["start"] == "Visible Start Leak Probe"
    assert archive_prompts[0]["end"] is None


def test_archive_search_matches_expired_end(cursor, archive_search_prompt_set):
    archive_prompts, num_prompts = prompts.get_archive_prompts("sprint", search="Expired End Needle")

    assert num_prompts == 1
    assert archive_prompts[0]["start"] == "Expired Start Needle"
    assert archive_prompts[0]["end"] == "Expired End Needle"


def test_archive_search_treats_like_wildcards_as_literals(cursor, archive_search_prompt_set):
    archive_prompts, num_prompts = prompts.get_archive_prompts("sprint", search="%")

    assert num_prompts == 0
    assert archive_prompts == []


def test_archive_search_treats_sql_syntax_as_literal_text(cursor, archive_search_prompt_set):
    archive_prompts, num_prompts = prompts.get_archive_prompts("sprint", search="' OR 1=1 --")

    assert num_prompts == 0
    assert archive_prompts == []
