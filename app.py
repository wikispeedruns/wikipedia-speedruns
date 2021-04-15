from flask import Flask, render_template, request, redirect
import db

app = Flask(__name__)
db.init_app(app)

# TODO fix this
app.config["DATABASE"] = "wikipedia_speedruns"

from prompts import prompt_api
from runs import run_api
app.register_blueprint(prompt_api)
app.register_blueprint(run_api)

# Front end pages
@app.route('/', methods=['GET'])
def get_home_page():
    return render_template('home.html')

@app.route('/random', methods=['GET'])
def get_random_prompt():
    # TODO this is insanely inefficient, it needs to sort the whole table!
    query = ("""
    SELECT prompt_id FROM prompts
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
    query = ("SELECT MAX(prompt_id) FROM prompts;")

    with db.get_db().cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchone()
        return redirect("/play/" + str(results[0]), code=302)


@app.route('/manage', methods=['GET'])
def get_manage_page():
    return render_template('manage.html')

@app.route('/prompt/<id>', methods=['GET'])
def get_prompt_page(id):
    run_id = request.args.get('run_id', '')
    
    if len(run_id) != 0:
        return render_template('prompt.html', prompt_id=id, run_id=run_id)
    else:
        return render_template('prompt.html', prompt_id=id)


@app.route('/play/<id>', methods=['GET'])
def get_play_page(id):
    return render_template('play.html', prompt_id=id)


