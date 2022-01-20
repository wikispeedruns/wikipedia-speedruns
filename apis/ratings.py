from flask import session, request, render_template, Blueprint, current_app, jsonify
from pymysql.cursors import DictCursor

from db import get_db

ratings_api = Blueprint("ratings", __name__, url_prefix="/api/ratings")


@ratings_api.get("")
def get_top_ratings():
    '''
    Gets the ratings of each user in order from highest to lowest
    TODO query params for the LIMIT/OFFSET
    '''


    # Only rate users with at least 3 rated competitions
    query = '''
    SELECT users.username, ratings.rating FROM ratings
    JOIN users ON users.user_id = ratings.user_id
    WHERE ratings.num_rounds >= 3
    ORDER by ratings.rating DESC
    LIMIT 10
    '''


    db = get_db()
    # Check if user exists, and either login or set session to create new account
    with get_db().cursor(cursor=DictCursor) as cursor:
        result = cursor.execute(query)
        return jsonify(cursor.fetchall())


