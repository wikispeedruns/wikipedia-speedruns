import pytest
import datetime
import json

from wikispeedruns import streaks


# Included user in dependency to lineup clean better
@pytest.fixture(autouse=True)
def cleanup(db, cursor, user):
    yield
    cursor.execute("DELETE FROM sprint_runs")
    db.commit()
    cursor.execute("DELETE FROM sprint_prompts")
    db.commit()


def add_prompts(cursor, user_id, days):
    prompt_query = """
    INSERT INTO `sprint_prompts` (`start`, `end`, `rated`, `active_start`, `active_end`)
    VALUES ("A", "B", 1, %s, %s);
    """
    runs_query = """
    INSERT INTO sprint_runs (prompt_id, user_id, start_time, end_time, path, finished, play_time)
    VALUES (%s, %s, %s, %s, %s, 1, 3600)
    """

    path = json.dumps({
        "version": "2.0",
        "path": [
            {"Article": "A"},
            {"Article": "B"}
        ]
    })

    for day_diff in days:
        now = datetime.date.today()
        dt = (now - datetime.timedelta(days=day_diff))

        # add prompt
        cursor.execute(prompt_query, (dt, dt + datetime.timedelta(days=1)))

        # Get prompt id
        cursor.execute("SELECT LAST_INSERT_ID() AS id")
        id = cursor.fetchone()["id"]

        # add run
        cursor.execute(runs_query, (id, user_id, dt + datetime.timedelta(hours=1), dt + datetime.timedelta(hours=2), path))



def test_streak_with_today(cursor, user):
    user_id = user["user_id"]
    add_prompts(cursor, user_id, [0, 1, 2, 3])
    res = streaks.get_current_streak(user_id)
    assert(res["streak"] == 4)
    assert(res["done_today"])


def test_streak_without_today(cursor, user):
    user_id = user["user_id"]
    add_prompts(cursor, user_id, [1, 2, 3])
    res = streaks.get_current_streak(user_id)
    assert(res["streak"] == 3)
    assert(not res["done_today"])



def test_streak_with_old_streak(cursor, user):
    user_id = user["user_id"]
    add_prompts(cursor, user_id, [1, 2, 3, 4, 10, 11, 12, 13])
    res = streaks.get_current_streak(user_id)
    assert(res["streak"] == 4)
    assert(not res["done_today"])


def test_streak_with_today_and_gap(cursor, user):
    user_id = user["user_id"]
    add_prompts(cursor, user_id, [0, 2, 3, 4, 10, 11, 12, 13])
    res = streaks.get_current_streak(user_id)
    assert(res["streak"] == 1)
    assert(res["done_today"])


def test_streak_without_today_and_gap(cursor, user):
    user_id = user["user_id"]
    add_prompts(cursor, user_id, [1, 3, 4, 10, 11, 12, 13])
    res = streaks.get_current_streak(user_id)
    assert(res["streak"] == 1)
    assert(not res["done_today"])
