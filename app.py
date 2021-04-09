from flask import Flask, render_template
import db

app = Flask(__name__)
db.init_app(app)

# TODO fix this
app.config["DATABASE"] = "wikipedia_speedruns"

from prompts import prompt_api
app.register_blueprint(prompt_api)

# Front end pages
@app.route('/', methods=['GET'])
def get_start():
    return render_template('start.html')


