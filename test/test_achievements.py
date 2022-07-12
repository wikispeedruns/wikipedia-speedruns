import pytest
import wikispeedruns

PROMPT = {
        "start" : "Wikipedia",
        "end" : "YouTube", 
        "prompt_id": 1
}

testData = {
    "end_time": "2022-05-27T10:22:25.446000",
    "path": [
      {
        "article": "Wikipedia",
        "loadTime": 0.169,
        "timeReached": 0.169
      },
      {
        "article": "Youtube",
        "loadTime": 0.135,
        "timeReached": 1.887
      }
    ],
    "play_time": 1.583,
    "finished": 1,
    "run_id": 11631,
    "start_time": "2022-05-27T10:22:23.559000"
}


@pytest.fixture
def add_achievements(cursor):
    wikispeedruns.achievements.add_all_achievements(cursor)
    yield
    assert 0 != cursor.execute("DELETE FROM list_of_achievements")


@pytest.fixture
def run_id(cursor, user):
    query = "INSERT INTO sprint_prompts (prompt_id, start, end) VALUES (%s, %s, %s);"
    cursor.execute(query, (PROMPT["prompt_id"], PROMPT["start"], PROMPT["end"]))

    query = """
    INSERT INTO sprint_runs 
    (start_time, end_time, play_time, finished, path, prompt_id, user_id)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s);
    """
    data = (testData["start_time"], testData["end_time"], testData["play_time"], 
    testData["finished"], testData["path"], PROMPT["prompt_id"], user["user_id"] 
    )
    cursor.execute(query, data)

    yield cursor.lastrowid

    cursor.execute("DELETE FROM sprint_runs")
    cursor.execute("DELETE FROM sprint_prompts")


def test_process_run(cursor, client, user, run_id):
    resp = client.post("/api/users/login", json={"username": user["username"], "password": user["password"]})

    resp = client.get(f"/api/achievements/process/{run_id}")
    assert resp.status_code == 200

    resp = client.get("/api/achievements/user")
    assert resp.status_code == 200
    assert resp.json["meta"]["achieved"] # achievement to reach Wikipedia

    query = "DELETE FROM achievements_progress"
    assert 0 != cursor.execute(query)

    client.post("/api/users/logout")