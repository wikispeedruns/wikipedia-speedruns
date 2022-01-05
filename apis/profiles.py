from pymysql.cursors import DictCursor
from flask import session, request, abort, Blueprint

from db import get_db

# TODO figure out a better name for this
profile_api = Blueprint("profiles", __name__, url_prefix="/api/profiles")


@profile_api.get("/<username>/")
def get_user_info(username):
    '''
    Get the basic info for a user
    TODO cache this?
    '''
    if (session.get("username") == username or session.get("admin")):
        query = "SELECT `username`, `email`, `email_confirmed`, `admin` FROM `users` WHERE `username`=%s"
    else:
        query = "SELECT `username`, `email_confirmed`, `admin` FROM `users` WHERE `username`=%s"


    with get_db().cursor(cursor=DictCursor) as cursor:
        num = cursor.execute(query, (username, ))
        if (num == 0): abort(404)

        result = cursor.fetchone()

    return result, 200


@profile_api.get("/<username>/totals")
def get_total_stats(username):
    '''
    Get the total number of prompts for a user
    TODO cache this?
    '''

    query = """
    SELECT users.user_id, COUNT(run_id) AS total_runs, COUNT(DISTINCT prompt_id) as total_prompts FROM users 
    LEFT JOIN runs ON runs.user_id=users.user_id 
    WHERE users.username=%s
    """
    
    with get_db().cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (username, ))

        result = cursor.fetchone()
        if (result["user_id"] is None): abort(404)
        result.pop("user_id")


    return result, 200
