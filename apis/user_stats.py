from pymysql.cursors import DictCursor
from flask import session, request, abort, Blueprint

from db import get_db

# TODO figure out a better name for this
stats_api = Blueprint("user_stats", __name__, url_prefix="/api/user_stats")


@stats_api.get("/<user_id>/totals")
def confirm_email_request(user_id):
    '''
    Get the total number of prompts for a user
    TODO cache this?
    '''

    query = """
    SELECT users.user_id, COUNT(run_id) AS total_runs, COUNT(DISTINCT prompt_id) as total_prompts FROM users 
    LEFT JOIN runs ON runs.user_id=users.user_id 
    WHERE users.user_id=%s
    """
    
    with get_db().cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (user_id, ))

        result = cursor.fetchone()
        if (result["user_id"] is None): abort(404)
        result.pop("user_id")


    return result, 200
