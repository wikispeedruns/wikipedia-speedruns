from pymysql.cursors import DictCursor
from flask import session, request, abort, Blueprint, jsonify
from util.decorators import check_user

from wikispeedruns import streaks

from db import get_db

# TODO figure out a better name for this
profile_api = Blueprint("profiles", __name__, url_prefix="/api/profiles")


@profile_api.get("/<username>")
def get_user_info(username):
    '''
    Get the basic info for a user
    TODO cache this?
    '''

    query = f'''
    SELECT
        username,
        email_confirmed,
        {'email,' if session.get("username") == username or session.get("admin") else ''}
        {'admin,' if session.get("admin") else ''}
        join_date,
        ratings.rating
    FROM users
    LEFT JOIN ratings ON ratings.user_id=users.user_id
    WHERE users.username=%s
    '''

    with get_db().cursor(cursor=DictCursor) as cursor:
        num = cursor.execute(query, (username, ))
        if (num == 0): abort(404)

        result = cursor.fetchone()

    return result, 200


@profile_api.get("/<username>/stats")
def get_total_stats(username):
    '''
    Get aggregate statistics for a user
    TODO cache this?
    '''

    query_sprints = """
    SELECT
        users.user_id,
        COUNT(run_id) AS total_runs,
        COUNT(case finished when 1 then 1 else null end) AS total_completed_runs,
        COUNT(DISTINCT prompt_id) as total_prompts
    FROM users
    LEFT JOIN sprint_runs ON sprint_runs.user_id=users.user_id
    WHERE users.username=%s
    """

    query_quick_runs = """
    SELECT
        COUNT(run_id) AS total_runs,
        COUNT(case finished when 1 then 1 else null end) AS total_completed_runs
    FROM users
    LEFT JOIN quick_runs ON quick_runs.user_id=users.user_id
    WHERE users.username=%s
    """

    with get_db().cursor(cursor=DictCursor) as cursor:
        cursor.execute(query_sprints, (username, ))

        result = cursor.fetchone()
        if (result["user_id"] is None): 
            return "Username not found", 404
        result.pop("user_id")

        cursor.execute(query_quick_runs, (username, ))
        result_quick_runs = cursor.fetchone()
        result["total_runs"] += result_quick_runs["total_runs"]
        result["total_completed_runs"] += result_quick_runs["total_completed_runs"]

    return result, 200


@profile_api.get("/streak")
@check_user
def get_current_streak():

    user_id = session['user_id']
    return jsonify(streaks.get_current_streak(user_id))
