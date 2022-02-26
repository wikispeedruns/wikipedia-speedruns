'''
Script that generates configuration for server, as well as adds admin account
'''

import json
import secrets

def create_prod_conf():
    config = {}
    config["SECRET_KEY"] = str(secrets.token_urlsafe(20))
    config["GOOGLE_OAUTH_CLIENT_ID"] = input("Google Client ID for Oauth: ")
    config["GOOGLE_OAUTH_CLIENT_SECRET"] = input("Google Secret for Oath: ")
    # TODO more here

    config["MAIL_SERVER"] = input("Mail Server URL: ")
    config["MAIL_PORT"] = input("Mail Server Port: ")
    config["MAIL_USERNAME"] = input("SMTP Username: ")
    config["MAIL_PASSWORD"] = input("SMTP Password: ")
    config["MAIL_DEFAULT_SENDER"] = input("Default Sender for mail: ")


    json.dump(config, open('../config/prod.json', 'w'), indent=4)


create_prod_conf()

