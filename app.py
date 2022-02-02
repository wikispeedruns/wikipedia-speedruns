from flask import Flask

import db
import mail
import tokens

import json


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_file('config/default.json', json.load)

    if test_config is None:
        # load prod settings if not testing and if they exist
        try:
            app.config.from_file('config/prod.json', json.load)
        except FileNotFoundError:
            pass
    else:
        app.config.update(test_config)

    db.init_app(app)
    mail.init_app(app)
    tokens.init_app(app)

    from apis.prompts import prompt_api
    from apis.runs import run_api
    from apis.users import user_api
    from apis.profiles import profile_api
    from apis.scraper import scraper_api
    from apis.ratings import ratings_api
    from views import views


    app.register_blueprint(prompt_api)
    app.register_blueprint(run_api)
    app.register_blueprint(user_api)
    app.register_blueprint(profile_api)
    app.register_blueprint(scraper_api)
    app.register_blueprint(ratings_api)

    app.register_blueprint(views)

    return app
