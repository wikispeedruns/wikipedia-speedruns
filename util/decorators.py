from flask import request, Response, jsonify, session

# Decorators that checks for admin (or returns 401)
# Needs to be preceded by a route
# @api.route(...)
def check_admin(endpoint_func):
    def wrapper(*args, **kwargs):
        if ('admin' not in session or not session['admin']):
            return 'Admin access required', 401

        return endpoint_func(*args, **kwargs)
    wrapper.__name__ = endpoint_func.__name__
    wrapper.__doc__ = endpoint_func.__doc__
    return wrapper

def check_user(endpoint_func):
    def wrapper(*args, **kwargs):
        if ('user_id' not in session):
            return 'User account required', 401

        return endpoint_func(*args, **kwargs)
    wrapper.__name__ = endpoint_func.__name__
    wrapper.__doc__ = endpoint_func.__doc__
    return wrapper

