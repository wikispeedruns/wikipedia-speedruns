from flask import Flask, render_template, request, redirect, session, url_for

import db
from util.decorators import check_admin

import json


app = Flask(__name__)

app.config.from_file('config/default.json', json.load)
# load prod settings if they exist
try:
    app.config.from_file('config/prod.json', json.load)
except FileNotFoundError:
    pass

db.init_app(app)

from prompts import prompt_api
from runs import run_api
from users import user_api
app.register_blueprint(prompt_api)
app.register_blueprint(run_api)
app.register_blueprint(user_api)



# Passes session args to function if needed
def render_with_user(template, **kwargs):
    if ("user_id" in session):
        return render_template(template, user_id=session["user_id"], username=session["username"], **kwargs)
    else:
        return render_template(template, **kwargs)

# Front end pages
@app.route('/', methods=['GET'])
def get_home_page():    
    return render_with_user('home.html')

@app.route('/random', methods=['GET'])
def get_random_prompt():
    # TODO this is insanely inefficient, it needs to sort the whole set of public prompts!
    query = ("""
    SELECT prompt_id FROM prompts
    WHERE public=TRUE
    ORDER BY RAND()
    LIMIT 1;
    """)

    with db.get_db().cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchone()
        print(results)
        return redirect("/play/" + str(results[0]), code=302)

@app.route('/latest', methods=['GET'])
def get_latest_prompt():
    # TODO its a little messy to do this here
    query = ("SELECT MAX(prompt_id) FROM prompts WHERE public=TRUE;")

    with db.get_db().cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchone()
        return redirect("/play/" + str(results[0]), code=302)

@app.route('/register', methods=['GET'])
def get_register_page():
    return render_with_user('register.html')

@app.route('/login', methods=['GET'])
def get_login_page():
    return render_with_user('login.html')

@app.route('/manage', methods=['GET'])
@check_admin
def get_manage_page():
    return render_with_user('manage.html')

@app.route('/prompt/<id>', methods=['GET'])
def get_prompt_page(id):
    run_id = request.args.get('run_id', '')
    
    if len(run_id) != 0:
        return render_with_user('prompt.html', prompt_id=id, run_id=run_id)
    else:
        return render_with_user('prompt.html', prompt_id=id)


@app.route('/play/<id>', methods=['GET'])
def get_play_page(id):
    return render_with_user('play.html', prompt_id=id)


