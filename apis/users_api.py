from datetime import datetime
from flask.helpers import url_for
import pymysql
from werkzeug.utils import redirect
from util.decorators import check_user
from flask import session, request, render_template, Blueprint, current_app, jsonify
import flask_dance.contrib.google as oauth_google
from flask_mail import Message

from db import get_db
from mail import mail
from tokens import (
    create_reset_token,
    verify_reset_token,
    create_confirm_token,
    verify_confirm_token
)

from pymysql.cursors import DictCursor

from wikispeedruns.auth import passwords

user_api = Blueprint("users", __name__, url_prefix="/api/users")

# Setup OAuth
google_bp = oauth_google.make_google_blueprint(redirect_url="/api/users/auth/google/check",
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]
)
# Note, url_prefix overrides the entire user_api prefix, not sure if this will get changed
user_api.register_blueprint(google_bp, url_prefix="/api/users/auth")


def _send_reset_email(id, email, username, hashed, url_root):
    token = create_reset_token(id, hashed)
    link = f"{url_root}reset/{id}/{token}"

    msg = Message("Reset Your Password - Wikispeedruns.com",
      recipients=[email])

    msg.body = f"Hello {username},\n\n You are receiving this email because we received a request to reset your password. If this wasn't you, you can ignore this email. Otherwise, please follow this link: {link}"
    msg.html = render_template('emails/reset.html', user=username, link=link)
    mail.send(msg)


def _send_confirmation_email(id, email, username, url_root, on_signup=False):
    token = create_confirm_token(id)
    link = url_root + "confirm/" + token

    msg = Message("Confirm your Email - Wikispeedruns.com", recipients=[email])

    msg.body = f"Hello {username},\n\nClick the following link to confirm your email: {link}"
    msg.html = render_template('emails/confirm.html', link=link, user=username, on_signup=on_signup)

    mail.send(msg)


def _valid_username(username):
    valid_char = lambda c: (c.isalnum() or c == '-' or c == '_' or c == '.')
    return all(map(valid_char, username))


def _login_session(user):
    session.clear()
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["admin"] = user["admin"] != 0
    session.permanent = True


def _logout_session():
    # Logout from oauth if there is oauth
    if (google_bp.token):
        token = google_bp.token["access_token"]
        resp = oauth_google.google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert resp.ok, resp.text
        del google_bp.token  # Delete OAuth token from storage


    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("admin", None)


@user_api.post("/create/oauth")
def create_user_oauth():
    """
    Example json input
    {
        "username" : "echoingsins"
    }
    """

    # We assume that the oauth service provides an email
    # TODO Save google account id?
    email = session["pending_oauth_creation"]
    username = request.json["username"]

    # Validate username
    if (not _valid_username(username)):
        return "Invalid username", 400

    query = "INSERT INTO `users` (`username`, `email`, `email_confirmed`, `join_date`) VALUES (%s, %s, %s, %s)"
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')

    db = get_db()
    with get_db().cursor() as cursor:
        try:
            result = cursor.execute(query, (username, email, True, date))
            db.commit()

        except pymysql.IntegrityError:
            return (f'User {username} already exists', 409)

    return f"User {username} added".format(username), 201


@user_api.post("/create/email")
def create_user():
    """
    Example json input
    {
        "username" : "echoingsins",
        "email" : "echoingsins@gmail.com",
        "password" : "lmao"
    }
    """

    if not all([field in request.json for field in ["username", "email", "password"]]):
        return "Invalid request", 400

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    # Validate username
    if (not _valid_username(username)):
        return "Invalid username", 400

    # Use SHA256 to allow for arbitrary length passwords
    hash = passwords.hash_password(password)
    query = "INSERT INTO `users` (`username`, `hash`, `email`, `email_confirmed`, `join_date`) VALUES (%s, %s, %s, %s, %s)"
    get_id_query = "SELECT LAST_INSERT_ID()"

    now = datetime.now()
    date = now.strftime('%Y-%m-%d')

    db = get_db()
    with get_db().cursor() as cursor:

        try:
            cursor.execute(query, (username, hash, email, False, date))

            cursor.execute(get_id_query)
            (id,) = cursor.fetchone()

            _send_confirmation_email(id, email, username, request.url_root, on_signup=True)

            db.commit()

        except pymysql.IntegrityError:
            return (f'User {username} already exists, or email {email} in use', 409)
        except pymysql.Error as e:
            return ("Unknown error", 500)

    return (f'User {username} ({id}) added', 201)


@user_api.get("/auth/google/check")
def check_google_auth():
    resp = oauth_google.google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    # TODO do something with google user id

    email = resp.json()["email"]
    query = "SELECT * from `users` WHERE `email`=%s"

    db = get_db()
    # Check if user exists, and either login or set session to create new account
    with get_db().cursor(cursor=DictCursor) as cursor:
        result = cursor.execute(query, (email))

        if (result == 0):
            session["pending_oauth_creation"] = email
        else:
            user = cursor.fetchone()
            _login_session(user)

    return redirect("/pending")


@user_api.post("/login")
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

    password = request.json["password"]

    db = get_db()
    with db.cursor(DictCursor) as cursor:
        # Query for user and check password
        result = cursor.execute(query, (login, ))

        if (result == 0):
            return "Incorrect username or password", 401

        user = cursor.fetchone()

        if not passwords.check_password(user, password):
            return "Incorrect username or password", 401

    # Add session
    _login_session(user)

    return "Logged in", 200



@user_api.post("/logout")
def logout():
    _logout_session()
    return "Logged out", 200


@user_api.post("/change_password")
@check_user
def change_password():
    '''
    Given the old password and a new one, change the password
    '''
    get_query = "SELECT * FROM `users` WHERE `user_id`=%s"
    update_query = "UPDATE `users` SET `hash`=%s WHERE `user_id`=%s"

    if ("old_password" not in request.json or "new_password" not in request.json):
        return ("Password(s) not in request", 400)

    id = session["user_id"]
    old_password = request.json["old_password"]
    new_password = request.json["new_password"]

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        # Query for user and check password
        result = cursor.execute(get_query, (id, ))

        # TODO , should be found

        user = cursor.fetchone()

        if not passwords.check_password(user, old_password):
            return "Incorrect password", 401

        new_hash = passwords.hash_password(new_password)

        cursor.execute(update_query, (new_hash, id))
        db.commit()

    return "Password Changed", 200



@user_api.post("/change_username")
@check_user
def change_username():
    '''
    Given a new username, change the username
    '''
    update_query = "UPDATE `users` SET `username`=%s WHERE `user_id`=%s"

    if ("new_username" not in request.json):
        #print("Incomplete request")
        return ("Incomplete request", 400)

    id = session["user_id"]
    new_username = request.json["new_username"]

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:

        try:
            cursor.execute(update_query, (new_username, id))
            db.commit()

        except pymysql.IntegrityError:
            print("dup username")
            return (f'Username `{new_username}` already exists', 409)
        except pymysql.Error as e:
            return ("Unknown error", 500)

    session["username"] = new_username
    return "Username Changed", 200



@user_api.post("/confirm_email_request")
@check_user
def confirm_email_request():
    '''
        Request another email token be sent in as a logged in user, i.e. from profile page
    '''
    id = session["user_id"]

    check_query = "SELECT `email_confirmed` FROM `users` WHERE `user_id`=%s"

    query = "SELECT `email`, `username` FROM `users` WHERE `user_id`=%s"

    db = get_db()
    with db.cursor() as cursor:
        res = cursor.execute(check_query, (id, ))
        if (res != 0):
            email_confirmed = cursor.fetchone()
            if email_confirmed[0] == 1:
                return "Email already confirmed", 400

        cursor.execute(query, (id, ))
        (email, username) = cursor.fetchone()
        # TODO throw error?

    _send_confirmation_email(id, email, username, request.url_root)

    return "New confirmation email sent", 200

@user_api.post("/confirm_email")
def confirm_email():
    token = request.json["token"]
    id = verify_confirm_token(token)

    if (id is None):
        return ("Invalid email confirmation link, could be outdated", 400)

    query = "UPDATE `users` SET `email_confirmed` = 1 WHERE `user_id`=%s"

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (id, ))
        db.commit()

        # TODO throw error if not right?

    return "Email Confirmed"


@user_api.post("/check_email_confirmation")
def check_email_confirmation():
    username = request.json

    # user must be logged in to access
    if session["username"] != username:
        return "Username does not match session", 400

    query = "SELECT `email_confirmed` FROM `users` WHERE `username`=%s"

    db = get_db()
    with db.cursor() as cursor:
        res = cursor.execute(query, (username, ))
        if (res != 0):
            email_confirmed = cursor.fetchone()
            if email_confirmed[0] == 1:
                return "true", 200

    return "false", 200


@user_api.post("/reset_password_request")
def reset_password_request():
    '''
    Request a password reset for a particular email. Will always return 200 as to not give away
    the existence of certain emails on the website
    '''

    email = request.json['email']

    query = "SELECT `user_id`, `username`, `hash` FROM `users` WHERE `email`=%s"

    db = get_db()
    with db.cursor() as cursor:
        res = cursor.execute(query, (email, ))

        if (res != 0):
            (id, username, hash) = cursor.fetchone()
            _send_reset_email(id, email, username, hash, request.url_root)

    return f"If the account for {email} exists, an email has been sent with a reset link", 200



@user_api.post("/reset_password")
def reset_password():
    '''
    Given the user id, reset token and a new password, change the password
    '''
    get_query = "SELECT hash FROM `users` WHERE `user_id`=%s"
    update_query = "UPDATE `users` SET `hash`=%s, `is_old_hash`=0 WHERE `user_id`=%s"

    if not all([field in request.json for field in ["user_id", "password", "token"]]):
        return "Invalid request", 400

    if type(request.json["user_id"]) != int:
        return "`user_id` should be an int"

    id = request.json["user_id"]
    password = request.json["password"]
    token = request.json["token"]


    db = get_db()
    with db.cursor() as cursor:
        # Query for user and use password to decode token
        result = cursor.execute(get_query, (id, ))

        if (result == 0):
            return "Invalid id", 400

        (old_hash, ) = cursor.fetchone()

        if (id != verify_reset_token(token, old_hash)):
            return "Invalid token", 400

        new_hash = passwords.hash_password(password)
        cursor.execute(update_query, (new_hash, id))
        # TODO check

        db.commit()

    return "Password Changed", 200



@user_api.delete("/delete_account")
@check_user
def delete_account():
    """
        Delete the account of the user in session
    """

    user_query1 = """
    delete from historical_ratings where user_id = %(user_id)s
    """
    user_query2 = """
    delete from ratings where user_id = %(user_id)s
    """
    user_query3 = """
    delete from sprint_runs where user_id = %(user_id)s
    """
    user_query4 = """
    delete from marathonruns where user_id = %(user_id)s
    """
    user_query5 = """
    delete from lobby_runs where user_id = %(user_id)s
    """
    user_query6 = """
    delete from user_lobbys where user_id = %(user_id)s
    """
    user_query7 = """
    delete from achievements_progress where user_id = %(user_id)s
    """
    user_query8 = """
    delete from quick_runs where user_id = %(user_id)s
    """
    user_query9 = """
    delete from users where user_id = %(user_id)s
    """

    get_hosted_lobbies_query = """
    select lobby_id from user_lobbys
    WHERE user_id=%(user_id)s AND owner = 1
    """

    delete_lobbies_query1 = """
    DELETE lobby_runs FROM lobby_runs
    WHERE lobby_runs.lobby_id=%s
    """
    delete_lobbies_query2 = """
    DELETE user_lobbys FROM user_lobbys
    WHERE user_lobbys.lobby_id=%s
    """
    delete_lobbies_query3 = """
    DELETE lobby_prompts FROM lobby_prompts
    WHERE lobby_prompts.lobby_id=%s
    """
    delete_lobbies_query4 = """
    DELETE lobbys FROM lobbys
    WHERE lobbys.lobby_id=%s
    """

    id = session["user_id"]
    args = {"user_id": id}

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:

        count = cursor.execute(get_hosted_lobbies_query, args)

        lobbies = cursor.fetchall()
        lobby_ids = [str(x['lobby_id']) for x in lobbies]

        if (count > 0):
            cursor.executemany(delete_lobbies_query1, lobby_ids)
            cursor.executemany(delete_lobbies_query2, lobby_ids)
            cursor.executemany(delete_lobbies_query3, lobby_ids)
            cursor.executemany(delete_lobbies_query4, lobby_ids)

        cursor.execute(user_query1, args)
        cursor.execute(user_query2, args)
        cursor.execute(user_query3, args)
        cursor.execute(user_query4, args)
        cursor.execute(user_query5, args)
        cursor.execute(user_query6, args)
        cursor.execute(user_query7, args)
        cursor.execute(user_query8, args)
        cursor.execute(user_query9, args)

        db.commit()

    return "User account deleted", 200

