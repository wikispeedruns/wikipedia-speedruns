from flask import Flask, render_template, request
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

@app.route('/prompt/<id>', methods=['GET'])
def get_prompt_page(id):
    run_id = request.args.get('run_id', '')
    
    if len(run_id) != 0:
        return render_template('prompt.html', prompt_id=id, run_id=id)
    else:
        return render_template('prompt.html', prompt_id=id)


@app.route('/play/<id>', methods=['GET'])
def get_play_page(id):
    return render_template('play.html', prompt_id=id)


