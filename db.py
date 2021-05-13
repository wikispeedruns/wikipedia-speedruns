import pymysql
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            user='user', 
            host='127.0.0.1', 
            database=current_app.config['DATABASE']
        )

    return g.db

def close_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()