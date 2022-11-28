import db
from app import create_app
from multiprocessing import Process

def run_with_app_context(func, args=()):
    app = create_app()
    
    with app.app_context():
        func(*args)

def run_with_db(func, conn, args=()):
    with db.use_instance_db(conn):
        func(*args)


def start_process(_target, _args=()):
    Process(target=run_with_app_context, args=(_target, _args)).start()

def start_process_with_db(_target, _args=()):
    Process(target=run_with_db, args=(_target, db.get_conn_info() , _args)).start()

