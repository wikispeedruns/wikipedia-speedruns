from app import create_app
from multiprocessing import Process

def run_with_app_context(func, args=()):
    app = create_app()
    
    with app.app_context():
        func(*args)

def start_process(_target, _args=()):
    Process(target=run_with_app_context, args=(_target, _args)).start()
