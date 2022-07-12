from flask import request, Blueprint, session
from util.decorators import check_user

import db
from db import get_db
from pymysql.cursors import DictCursor

from wikispeedruns import achievements

achievements_api = Blueprint('achievements', __name__, url_prefix='/api/achievements')


@achievements_api.get('/process/<int:run_id>')
def process_for_achievements(run_id):

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        query = "SELECT * FROM sprint_runs WHERE run_id = (%s)"
        if cursor.execute(query, (run_id, )) == 0:
            return f"Cannot find run with run_id {run_id}", 404
        
        run_data = cursor.fetchone()
        if run_data["counted_for_am"]:
            return f"run_id {run_id} already counted for achievements", 400

        new_achievements = achievements.get_and_update_new_achievements(cursor, run_data)

        db.commit()

    return new_achievements



@achievements_api.get('/user')
@check_user
def get_all_achievements():
    user_id = session["user_id"]
    with get_db().cursor(cursor=DictCursor) as cursor:
        all_achievements = achievements.get_all_achievements_and_progress(cursor, user_id)
    return all_achievements




