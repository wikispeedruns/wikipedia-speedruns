'''
Script that generates configuration for server, as well as adds admin account
'''

import json
import secrets
import hashlib
import bcrypt
from getpass import getpass

import pymysql


def create_prod_conf():
    config = {}
    config["SECRET_KEY"] = str(secrets.token_urlsafe(20))

    # TODO more here

    json.dump(config, open('../config/prod.json', 'w'))

def create_admin_account():
    config = json.load(open('../config/default.json'))

    # load prod settings if they exist
    try:
        config.update(json.load(open('config/prod.json')))
    except FileNotFoundError:
        pass

    # Get admin username and password
    username = input("Admin account username (leave blank for 'admin'): " )
    if not username:
        username = 'admin'
    username = username

    email = input("Admin account email (currently not used): ")

    while(True):
        password = getpass("Admin account password: ")
        if password == getpass("Reenter password: "): break
        print("Passwords do not match!")

    password = password.encode()
    hash = bcrypt.hashpw(hashlib.sha256(password).digest(), bcrypt.gensalt())


    query = "INSERT INTO `users` (`username`, `hash`, `email`, `email_confirmed`, `admin`) VALUES (%s, %s, %s, %s, %s)"

    db = pymysql.connect(
            user=config["MYSQL_USER"], 
            host=config["MYSQL_HOST"],
            password=config["MYSQL_PASSWORD"], 
            database=config['DATABASE']
    )

    with db.cursor() as cursor:
        result = cursor.execute(query, (username, hash, email, True, True))

        if (result == 0):
            print("User {} already exists".format(username))
        else:
            print("Admin User {} added".format(username))
        db.commit()
    db.close()


ans = input("Would you like to setup configuration for production? (y/n): ")
if (ans == "y"):
    create_prod_conf()

ans = input("Would you like to setup an admin account? (y/n): ")

while (ans == "y"):
    create_admin_account()
    ans = input("Would you like to setup another admin account? (y/n): ")