from pymysql.cursors import DictCursor
from flask import session, request, abort, Blueprint, jsonify
from util.decorators import check_user

from db import get_db

# TODO figure out a better name for this
profile_api = Blueprint("profiles", __name__, url_prefix="/api/profiles")


@profile_api.get("/<username>/")
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

    query = """
    SELECT 
        users.user_id, 
        COUNT(run_id) AS total_runs, 
        COUNT(DISTINCT prompt_id) as total_prompts
    FROM users
    LEFT JOIN sprint_runs ON sprint_runs.user_id=users.user_id 
    WHERE users.username=%s
    """
    
    with get_db().cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (username, ))

        result = cursor.fetchone()
        if (result["user_id"] is None): abort(404)
        result.pop("user_id")


    return result, 200


@profile_api.get("/streak")
@check_user
def get_current_streak():
    
    user_id = session['user_id']
    ## NASTY NASTY SQL QUERY, COULD USE CLEAN UP
    query = """
    SELECT IF(run_date=CURDATE(), 1, 0) as done_today, count(*) as streak FROM ( 
        SELECT 
            run_date, 
            DATEDIFF(CURDATE(), run_date) AS Diff, 
            ROW_NUMBER() OVER(ORDER BY(run_date) DESC) AS rown 
        FROM (  
            SELECT 
                CAST(start_time AS DATE) as run_date
            FROM sprint_runs
            INNER JOIN sprint_prompts ON sprint_prompts.prompt_id = sprint_runs.prompt_id
            WHERE
                user_id=%s 
                AND sprint_runs.start_time BETWEEN sprint_prompts.active_start AND sprint_prompts.active_end
                AND rated
                AND end_time IS NOT NULL
            GROUP BY run_date
            ORDER BY run_date DESC ) 
        as temp) 
    as temp2 WHERE Diff <= rown
    """ 
    
    with get_db().cursor(cursor=DictCursor) as cursor:
        result = cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchone())
