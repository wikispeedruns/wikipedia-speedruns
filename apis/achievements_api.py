from flask import request, Blueprint, session
from util.decorators import check_user

import db
from db import get_db
from pymysql.cursors import DictCursor

from wikispeedruns import achievements

achievements_api = Blueprint('achievements', __name__, url_prefix='/api/achievements')


@achievements_api.patch('/process/<int:run_id>')
def process_for_achievements(run_id):

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        query = "SELECT * FROM sprint_runs WHERE run_id = (%s)"
        if cursor.execute(query, (run_id, )) == 0:
            return f"Cannot find run with run_id {run_id}", 404
        
        run_data = cursor.fetchone()
        if run_data["counted_for_am"]:
            return f"run_id {run_id} already counted for achievements", 400
        elif not achievements.check_data(run_data):
            return f"run data is not compatible for achievements", 400

        new_achievements = achievements.get_and_update_new_achievements(cursor, run_data)

        db.commit()

    return new_achievements, 200



@achievements_api.get('/user/<username>')
def get_all_achievements(username):
    with get_db().cursor(cursor=DictCursor) as cursor:
        rows = cursor.execute(f"SELECT user_id FROM users WHERE username = '{username}'")
        if rows == 0:
            return "User not found", 404
        user_id = cursor.fetchone()["user_id"]
        all_achievements = achievements.get_all_achievements_and_progress(cursor, user_id)
    return all_achievements, 200




