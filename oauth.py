from flask import current_app, g

from oauthlib.oauth2 import WebApplicationClient

GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

def init_app(app):
    app.teardown_appcontext(close_oauth)

def get_oauth():
    if 'oauth' not in g:
        g.oauth = WebApplicationClient(current_app.config["GOOGLE_CLIENT_ID"])

    return g.oauth

def close_oauth(exception):
    oauth = g.pop('oauth', None)

    if oauth is not None:
        oauth.close()