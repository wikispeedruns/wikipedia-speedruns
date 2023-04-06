from flask import request, Blueprint, session, jsonify
from util.decorators import check_user, check_request_json, check_admin

import db
from db import get_db
from pymysql.cursors import DictCursor
from datetime import datetime

from wikispeedruns import prompts

community_prompts_api = Blueprint('community_prompts', __name__, url_prefix='/api/community_prompts')


@community_prompts_api.post('/submit_sprint_prompt')
@check_user
@check_request_json({"start": str, "end": str, "anonymous": bool})
def submit_sprint_prompt():
    '''
    Add a sprint prompt to the pending pool
    '''
    query = "INSERT INTO cmty_pending_prompts_sprints (start, end, user_id, submitted_time, anonymous) VALUES (%(start)s, %(end)s, %(user_id)s, %(submitted_time)s, %(anonymous)s);"
    sel_query = "SELECT LAST_INSERT_ID()"

    user_id = session['user_id']
    
    query_args = {
        'start': request.json['start'],
        'end': request.json['end'],
        'user_id': user_id,
        'submitted_time': datetime.now(),
        'anonymous': request.json['anonymous']
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


@community_prompts_api.get('/get_pending_sprints')
@check_admin
def get_all_pending_sprints():
    query = """
    SELECT pending_prompt_id, start, end, submitted_time, anonymous, username FROM cmty_pending_prompts_sprints
    LEFT JOIN users
    ON users.user_id = cmty_pending_prompts_sprints.user_id
    """
    
    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)
    

@community_prompts_api.post('/approve_sprint')
@check_admin
@check_request_json({"pending_id": int, "anonymous": int})
def approve_sprint():
    
    pending_id = request.json['pending_id']
    anonymous = request.json['anonymous']
        
    query = """
    SELECT pending_prompt_id, start, end, submitted_time, anonymous, user_id FROM cmty_pending_prompts_sprints
    WHERE pending_prompt_id = %s
    """
    
    del_query = f"DELETE FROM cmty_pending_prompts_sprints WHERE pending_prompt_id = {pending_id};"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (pending_id, ))
        result = cursor.fetchone()
        new_prompt_id = prompts.add_community_sprint_prompt(
            result['start'], 
            result['end'], 
            result['user_id'], 
            result['submitted_time'], 
            anonymous
        )
        cursor.execute(del_query)
        db.commit()
        return jsonify({"new_prompt_id": new_prompt_id})
    
    
@community_prompts_api.delete('/reject_sprint')
@check_admin
@check_request_json({"pending_id": int})
def reject_sprint():
    
    pending_id = request.json['pending_id']
        
    query = f"DELETE FROM cmty_pending_prompts_sprints WHERE pending_prompt_id = {pending_id};"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        db.commit()
        return f'Deleted pending prompt {pending_id}', 200