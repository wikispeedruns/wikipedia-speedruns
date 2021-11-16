from flask import Flask

import db
import mail
import tokens
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
mail.init_app(app)
tokens.init_app(app)

from apis.prompts import prompt_api
from apis.runs import run_api
from apis.users import user_api
app.register_blueprint(prompt_api)
app.register_blueprint(run_api)
app.register_blueprint(user_api)

import routes