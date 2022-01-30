from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session
import json

from db import get_db
from pymysql.cursors import DictCursor


from wikispeedruns.marathon import genPrompts

marathon_api = Blueprint('marathon', __name__, url_prefix='/api/marathon')


@marathon_api.post('/runs/')
def create_run():
    query = "INSERT INTO `marathonruns` (`path`, `prompt_id`, `user_id`, `checkpoints`) VALUES (%s, %s, %s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    # datetime wants timestamp in seconds since epoch
    path = json.dumps(request.json['path'])
    checkpoints = json.dumps(request.json['checkpoints'])
    
    print(checkpoints)
    
    prompt_id = request.json['prompt_id']

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (path, prompt_id, user_id, checkpoints)))
        result = cursor.execute(query, (path, prompt_id, user_id, checkpoints))
        
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify(id)

    return "Error submitting prompt"


@marathon_api.post('/add/')
@check_admin
def create_marathon_prompt():
    
    print("Received marathon prompt req")
    print(request.json)
    
    query = "INSERT INTO `marathonprompts` (start, initcheckpoints, seed, checkpoints) VALUES (%s, %s, %s, %s);"

    nbucket = int(request.json.get("nbucket"))
    nbatch = int(request.json.get("nbatch"))
    nperbatch = int(request.json.get("nperbatch"))
    
    if nbucket < 1 or nbatch < 1 or nperbatch < 1:
        raise ValueError("Bad input")
    
    
    start = request.json.get("start")
    cp1 = request.json.get("cp1")
    cp2 = request.json.get("cp2")
    cp3 = request.json.get("cp3")
    cp4 = request.json.get("cp4")
    cp5 = request.json.get("cp5")
    seed = request.json.get("seed")
    
    initcheckpoints = [cp1, cp2, cp3, cp4, cp5]
    
    print("Starting prompt generation")
    
    checkpoints = genPrompts(initcheckpoints, batches=nbatch, nPerBatch=nperbatch, buckets=nbucket)

    print("Finished prompt generation")

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, json.dumps(initcheckpoints), seed, json.dumps(checkpoints)))
        db.commit()
        return "Prompt added!"



@marathon_api.delete('/delete/<id>')
@check_admin
def delete_prompt(id):
    query = "DELETE FROM marathonprompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(query, (id))
            db.commit()
            return "Prompt deleted!", 200
        
        except pymysql.IntegrityError:
            return "Integrity error, prompt may already have run(s)", 400
    

@marathon_api.get('/all')
def get_all_marathon_prompts():
    query = """
    SELECT * FROM marathonprompts
    """

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results)




@marathon_api.get('/prompt/<id>')
def get_marathon_prompt(id):
    
    query = "SELECT * FROM marathonprompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        prompt = cursor.fetchone()

        # Check permissions for users
        if (not session.get("admin")):
            if (prompt["type"] == "unused"):
                return "You do not have permission to view this prompt", 401
                    
        return jsonify(prompt)
