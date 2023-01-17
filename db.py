import pymysql
from flask import current_app, g
from contextlib import contextmanager

_instance_db = None

def init_app(app):
    app.teardown_appcontext(close_db)

def get_conn_info():
    return {
        'user' : current_app.config["MYSQL_USER"],
        'host' : current_app.config["MYSQL_HOST"],
        'password' : current_app.config["MYSQL_PASSWORD"],
        'database' : current_app.config['DATABASE'] 
    }

# Keep up to date with scripts/schema.sql
def get_db_version():
    return '2.4'

def get_db():
    if _instance_db:
        return _instance_db
        
    if 'db' not in g:
        g.db = pymysql.connect(**get_conn_info())

    return g.db

def close_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@contextmanager
def use_instance_db(conn):
    """
    Usage: 
    with use_instance_db(conn) as db:
        do stuff with db
    """
    try:
        global _instance_db
        _instance_db = pymysql.connect(**conn)
        yield _instance_db
    finally:
        if _instance_db is not None:
            _instance_db.close()