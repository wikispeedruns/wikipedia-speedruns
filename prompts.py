from flask import Flask, jsonify, request, Blueprint

from db import get_db
from pymysql.cursors import DictCursor

prompt_api = Blueprint('prompts', __name__, url_prefix='/api/prompt')


@prompt_api.route('/create', methods=['POST'])
def create_prompt():
    query = "INSERT INTO `prompts` (`start`, `end`) VALUES (%s, %s)"

    start = request.json['start']
    end = request.json['end']

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, end))
        db.commit()

        return "Prompt added!"

    return "Error adding prompt"


@prompt_api.route('/get', methods=['GET'])
def get_all_prompts():
    query = "SELECT * FROM `prompts`"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)

