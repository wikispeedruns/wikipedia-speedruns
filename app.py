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
from apis.profiles import profile_api
from apis.marathon import marathon_api
from apis.scraper import scraper_api
from apis.ratings import ratings_api

app.register_blueprint(prompt_api)
app.register_blueprint(run_api)
app.register_blueprint(user_api)
app.register_blueprint(profile_api)
app.register_blueprint(marathon_api)
app.register_blueprint(scraper_api)
app.register_blueprint(ratings_api)

import routes
