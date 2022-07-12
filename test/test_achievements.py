import pytest
import wikispeedruns

PROMPT_A = {
        "start" : "Wikipedia",
        "end" : "YouTube",
        "prompt_id": 30
}

testData = {
    "end_time": "2022-05-27T10:22:25.446000",
    "path": {
        'path':[
        {
            'article': 'Wikipedia',
            'loadTime': 0.169,
            'timeReached': 0.169
        },
        {
            'article': 'Youtube',
            'loadTime': 0.135,
            'timeReached': 1.887
        }
        ],
        'version': '2.1'
    },
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



def test_achievement(cursor, client, user):

    # Set up a prompt and a run, get the run_id
    query = "INSERT INTO sprint_prompts (prompt_id, start, end) VALUES (%s, %s, %s);"
    cursor.execute(query, (PROMPT_A["prompt_id"], PROMPT_A["start"], PROMPT_A["end"]))

    query = """
    INSERT INTO sprint_runs 
    (start_time, end_time, play_time, finished, path, prompt_id, user_id)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s);
    """
    data = (testData["start_time"], testData["end_time"], testData["play_time"], 
    testData["finished"], testData["path"], PROMPT_A["prompt_id"], user["user_id"] 
    )
    cursor.execute(query, data)
    run_id = cursor.lastrowid

    # Make sure currently we are logged in
    resp = client.post("/api/users/login", json={"username": user["username"], "password": user["password"]})


    # Go through some achievements procedure
    resp = client.get(f"/api/achievements/process/{run_id}")
    assert resp.status_code == 200

    resp = client.get("/api/achievements/user")
    assert resp.status_code == 200
    assert resp.json["meta"]["achieved"] # achievement to reach Wikipedia


    # delete everything added here
    query = "DELETE FROM achievements_progress"
    client.post("/api/users/logout")
    cursor.execute(f"DELETE FROM sprint_runs WHERE run_id={run_id}")
    cursor.execute("DELETE FROM sprint_prompts WHERE prompt_id={}".format(PROMPT_A["prompt_id"]))