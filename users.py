from flask import session, request, Blueprint

from db import get_db
from pymysql.cursors import DictCursor

import bcrypt
import hashlib

user_api = Blueprint("users", __name__, url_prefix="/api/users")

@user_api.route("/create", methods=["POST"])
def create_user():
    """
    Example json input
    {
        "username" : "echoingsins"
        "email" : "echoingsins@gmail.com    
        "password" : "lmao"
    }
    """

    if not all([field in request.json for field in ["username", "email", "password"]]):
        return "Invalid request", 400

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"].encode() # TODO ensure charset is good

    # Use SHA256 to allow for arbitrary length passwords
    hash = bcrypt.hashpw(hashlib.sha256(password).digest(), bcrypt.gensalt())
    query = "INSERT INTO `users` (`username`, `hash`, `email`, `email_confirmed`) VALUES (%s, %s, %s, %s)"
    print(hash)


    db = get_db()
    with get_db().cursor() as cursor:
        result = cursor.execute(query, (username, hash, email, False))

        if (result == 0):
            return ("User {} already exists".format(username), 409)

        db.commit()

    return ("User {} added".format(username), 201)




@user_api.route("/login", methods=["POST"])
def login():
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

    # Validate request and pull fields
    if ("email" in request.json):
        query = "SELECT * FROM `users` WHERE `email`= %s"
        login = request.json["email"]
    elif ("username" in request.json):
        query = "SELECT * FROM `users` WHERE `username`= %s"
        login = request.json["username"]
    else:
        return ("Username/email not in request", 400)

    if ("password" not in request.json):
        return ("Password not in request", 400)
    
    password = request.json["password"].encode()

    db = get_db()
    with db.cursor(DictCursor) as cursor:
        # Query for user and check password
        result = cursor.execute(query, (login, ))

        if (result == 0):
            return "Bad username or password", 401

        user = cursor.fetchone()
        hash = user["hash"].encode()

        if not bcrypt.checkpw(hashlib.sha256(password).digest(), hash):
            return "Bad username or password", 401

    # Add session
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["admin"] = user["admin"] != 0

    return "Logged in", 200



@user_api.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("admin", None)
    return "Logged out", 200