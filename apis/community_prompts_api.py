from flask import request, Blueprint, session
from util.decorators import check_user, check_request_json

import db
from db import get_db
from pymysql.cursors import DictCursor
from datetime import datetime

community_prompts_api = Blueprint('community_prompts', __name__, url_prefix='/api/community_prompts')


@community_prompts_api.post('/submit_sprint_prompt')
@check_user
@check_request_json({"start": str, "end": str})
def submit_sprint_prompt():
    '''
    Add a sprint prompt to the pending pool
    '''
    query = "INSERT INTO cmty_pending_prompts_sprints (start, end, user_id, submitted_time) VALUES (%(start)s, %(end)s, %(user_id)s, %(submitted_time)s);"
    sel_query = "SELECT LAST_INSERT_ID()"

    user_id = session['user_id']
    
    query_args = {
        'start': request.json['start'],
        'end': request.json['end'],
        'user_id': user_id,
        'submitted_time': datetime.now()
    }

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, query_args)
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return f'Added run {id} to cmty pending sprints', 200


@community_prompts_api.post('/submit_marathon_prompt')
@check_user
#@check_request_json({"start": str, "end": str})
def submit_marathon_prompt():
    '''
    Add a marathon prompt to the pending pool, TODO
    '''
    return 'Not implemented', 500