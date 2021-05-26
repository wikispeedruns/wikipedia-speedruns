from flask import Flask, jsonify, request, Blueprint

from db import get_db
from pymysql.cursors import DictCursor

import bcrypt
import hashlib

user_api = Blueprint('attempt', __name__, url_prefix='/api/users')

@user_api.route('/create', methods=['POST'])
def create_run():
    """
    Example json input
    {
        "username" : "echoingsins"
        "email" : "echoinsins@gmail.com    
        "password" : "lmao"
    }
    """

    if not all([field not in request.json for field in ["username", "email", "password"]]):
        return "Invalid request", 400

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    # Use SHA256 to allow for arbitrary length passwords
    hash = bcrypt.hashpw(hashlib.sha256(password).digest(). bcrypt.gensalt()) 
    query = "INSERT INTO `users` (`username`, `hash`, `email`, `email_confirmed`) VALUES (%s, %s, %s, %b)"


@user_api.route('/login', methods=['POST'])
def create_run():
    """
    Example json input
    {
        "username" : "echoingsins"
        "password" : "lmao"
    }

    OR 

    {
        "email" : "echoingsins@gmail.com"
        "password" : "lmao"
    }
    """


    if ("email" in request.json):
        query = "SELECT * FROM `users` WHERE `email`= (%s)"


    db = get_db()
    with db.cursor() as cursor:


    if not bcrypt.checkpw(password.encode('utf-8'), user['hashed']):
        return jsonify({'msg': 'Bad username or password'}), 401




