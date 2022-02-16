from flask import request, Response, jsonify, session
from typing import Dict

# Decorators that checks for admin (or returns 401)
# Needs to be preceded by a route
# @api.route(...)
def check_admin(endpoint_func):
    def wrapped(*args, **kwargs):
        if ('admin' not in session or not session['admin']):
            return 'Admin access required', 401

        return endpoint_func(*args, **kwargs)
    wrapped.__name__ = endpoint_func.__name__
    wrapped.__doc__ = endpoint_func.__doc__
    return wrapped

def check_user(endpoint_func):
    def wrapped(*args, **kwargs):
        if ('user_id' not in session):
            return 'User account required', 401

        return endpoint_func(*args, **kwargs)
    wrapped.__name__ = endpoint_func.__name__
    wrapped.__doc__ = endpoint_func.__doc__
    return wrapped


class RequestJsonError(Exception):
     pass


def check_request_json(expected: Dict[str, type]):
    
    def check(expected, reqjson):
        for k in expected:
            if (k not in reqjson):
                raise RequestJsonError(f"argument {k} missing")

            if (expected[k] != type(reqjson[k])):
                raise RequestJsonError(f"argument '{k}' expected '{expected[k].__name__}' but got '{type(reqjson[k]).__name__}'")

            if (expected[k] == dict):
                check(expected[k], reqjson[k])


    def wrapper(endpoint_func):
        def wrapped(*args, **kwargs):
            try:
                check(expected, request.json)
            except RequestJsonError as e:
                return f"Invalid Request: {e.args[0]}", 400

            return endpoint_func(*args, **kwargs)
            


        wrapped.__name__ = endpoint_func.__name__
        wrapped.__doc__ = endpoint_func.__doc__
        return wrapped

    return wrapper