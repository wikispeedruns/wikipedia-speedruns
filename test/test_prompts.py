import enum
import pytest

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
