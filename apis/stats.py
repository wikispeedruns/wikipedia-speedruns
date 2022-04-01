import gzip
import json

from flask import Blueprint, jsonify, make_response
from pymysql.cursors import DictCursor

from util.decorators import check_admin
from util.flaskjson import CustomJSONEncoder
from db import get_db

stats_api = Blueprint("stats", __name__, url_prefix="/api/stats")

@check_admin
@stats_api.get("/totals")
def get_total_stats():
    queries = {}
    queries['total_users'] = "SELECT COUNT(*) AS users_total FROM users"
    queries['total_google_users'] = 'SELECT COUNT(*) AS goog_total FROM users WHERE hash=""'
    queries['total_runs'] = "SELECT COUNT(*) AS sprints_total FROM sprint_runs"
    queries['total_finished_runs'] = "SELECT COUNT(*) AS sprints_finished FROM sprint_runs WHERE end_time IS NOT NULL"
    queries['total_user_runs'] = "SELECT COUNT(*) AS user_runs FROM sprint_runs WHERE user_id IS NOT NULL"
    queries['total_finished_user_runs'] = "SELECT COUNT(*) AS user_finished_runs FROM sprint_runs WHERE user_id IS NOT NULL AND end_time IS NOT NULL"
    results = {}

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        for _, query in queries.items():
            cursor.execute(query)
            results.update(cursor.fetchall()[0])
        return jsonify(results)


@check_admin
@stats_api.get("/daily")
def get_daily_stats():
    queries = {}
    queries['daily_new_users'] = '''
    WITH data AS (
        SELECT 
            DATE(join_date) AS day,
            COUNT(*) AS daily_users 
        FROM users
        GROUP BY day 
    )

    SELECT
        day,
        daily_users,
        SUM(daily_users) OVER (ORDER BY day) AS total 
    FROM data
    '''

    queries['daily_plays'] = '''
    WITH data AS (
        SELECT 
            DATE(start_time) AS day,
            COUNT(*) AS daily_plays 
        FROM sprint_runs
        WHERE start_time IS NOT NULL
        GROUP BY day 
    )

    SELECT
        day,
        daily_plays,
        SUM(daily_plays) OVER (ORDER BY day) AS total 
    FROM data
    '''
        
    queries['daily_finished_plays'] = '''
    WITH data AS (
        SELECT 
            DATE(start_time) AS day,
            COUNT(*) AS daily_plays 
        FROM sprint_runs
        WHERE start_time IS NOT NULL AND end_time IS NOT NULL
        GROUP BY day 
    )

    SELECT
        day,
        daily_plays,
        SUM(daily_plays) OVER (ORDER BY day) AS total 
    FROM data
    '''

    queries['avg_user_plays'] = '''
    WITH data AS (
        SELECT user_id,
        DATE(start_time) AS day,
        COUNT(*) AS plays
        FROM sprint_runs
        WHERE user_id IS NOT NULL AND start_time IS NOT NULL
        GROUP BY user_id, day
    )

    SELECT
        day,
        AVG(plays) AS "plays_per_user"
    FROM data
    GROUP BY day
    '''

    queries['active_users'] = '''
    WITH data AS (
        SELECT
            COUNT(*) AS plays,
            DATE(end_time) AS day,
            user_id
        FROM sprint_runs
        WHERE user_id IS NOT NULL AND end_time IS NOT NULL
        GROUP BY user_id, day
    )

    SELECT 
        day,
        COUNT(*) AS active_users
    FROM data
    GROUP BY day
    '''
    results = {} 

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        for name, query in queries.items():
            cursor.execute(query)
            results[name] = cursor.fetchall()
    
    content = gzip.compress(json.dumps(results, cls=CustomJSONEncoder).encode('utf8'), compresslevel=5)
    response = make_response(content)
    response.headers['Content-Length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'

    return response
