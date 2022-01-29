from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session
import json

from db import get_db
from pymysql.cursors import DictCursor

import time

from wikispeedruns.marathon import genPrompts

import random

marathon_api = Blueprint('marathon', __name__, url_prefix='/api/marathon')

"""
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


@marathon_api.post('/getcheckpoint/')
def get_new_checkpoint():

    distFromSecondMidpoint = 1

    checkpoints = [request.json['cp0'],
                   request.json['cp1'],
                   request.json['cp2'],
                   request.json['cp3'],
                   request.json['cp4']]
    
    seed = request.json['seed']
    
    List = [0, 1, 2, 3, 4]
    points = random.sample(List, 3)
    
    
    firstPair = bidirectionalSearch.findPaths(checkpoints[points[0]], checkpoints[points[1]])
    firstInd = int(len(firstPair[0][0]) / 2)
    midpoint = bidirectionalSearch.convertToArticleName(firstPair[0][0][firstInd])
    
    print(midpoint)
    
    secondPair = bidirectionalSearch.findPaths(midpoint, checkpoints[points[2]])
    secondInd = int(len(secondPair[0][0]) / 2)
    secondmidpoint = bidirectionalSearch.convertToArticleName(secondPair[0][0][secondInd])    
    
    print(secondmidpoint)
    
    final = genPrompts.traceFromStart(bidirectionalSearch.convertToID(secondmidpoint), distFromSecondMidpoint)[-1]
    
    finalTitle = bidirectionalSearch.convertToArticleName(final)

    print(finalTitle)

    return jsonify({"checkpoint":finalTitle})"""
    
    
    
@marathon_api.get('/getmarathonprompt/')
def get_marathon_prompt():
    return jsonify(genPrompts())