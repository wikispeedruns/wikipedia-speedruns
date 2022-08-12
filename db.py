import pymysql
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)

# Keep up to date with scripts/schema.sql
def get_db_version():
    return '2.2'

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            user=current_app.config["MYSQL_USER"], 
            host=current_app.config["MYSQL_HOST"],
            password=current_app.config["MYSQL_PASSWORD"], 
            database=current_app.config['DATABASE']
        )

    return g.db

def close_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()