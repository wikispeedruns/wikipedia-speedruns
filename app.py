from flask import Flask

import json

import db
import mail
import tokens
from util.flaskjson import CustomJSONEncoder

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from wikispeedruns import lobbys
def create_app(test_config=None):

    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    app.config.from_file('config/default.json', json.load)

    if test_config is None:
        # load prod settings if not testing and if they exist
        try:
            app.config.from_file('config/prod.json', json.load)
        except FileNotFoundError:
            pass
    else:
        app.config.update(test_config)


    # Setup monitoring if enabled
    if (app.config.get("SENTRY_ENABLED")):
        sentry_sdk.init(
            dsn="https://3fcc7c6b479248c8ac9839aad0440cba@o1133616.ingest.sentry.io/6180332",
            integrations=[FlaskIntegration()],
            # Set percent of things that are traced
            traces_sample_rate=0
        )


    db.init_app(app)
    mail.init_app(app)
    tokens.init_app(app)

    from apis.sprints import sprint_api
    from apis.runs import run_api
    from apis.users import user_api
    from apis.profiles import profile_api
    from apis.scraper import scraper_api
    from apis.ratings import ratings_api
    from apis.stats import stats_api
    from apis.marathon import marathon_api
    from apis.lobbys import lobby_api
    from views import views

    app.register_blueprint(sprint_api)
    app.register_blueprint(run_api)
    app.register_blueprint(user_api)
    app.register_blueprint(profile_api)
    app.register_blueprint(scraper_api)
    app.register_blueprint(ratings_api)
    app.register_blueprint(stats_api)
    app.register_blueprint(marathon_api)
    app.register_blueprint(lobby_api)
    app.register_blueprint(views)

    return app
