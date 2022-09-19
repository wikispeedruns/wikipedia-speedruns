import re
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


# Wrapper for optinal arg
# Kind of accidnetally building our own type system here oops
class OptionalArg():
    def __init__(self, base_type):
        self.base_type = base_type


def check_json(schema, reqjson):
    for k in reqjson:
        if k not in schema:
            raise RequestJsonError(f"Extraneous argument {k}")


    for k in schema:
        expected_type = schema[k]

        if (k not in reqjson):
            if (type(expected_type) == OptionalArg):
                continue
            else:
                raise RequestJsonError(f"argument {k} missing")

        if (type(expected_type) == OptionalArg):
            expected_type = expected_type.base_type

        if (type(expected_type) == list):
            for entry in reqjson[k]:
                check_json(expected_type[0], entry)
            continue

        if (type(expected_type) == dict):
            check_json(expected_type, reqjson[k])
            continue

        if (expected_type != type(reqjson[k])):
            raise RequestJsonError(f"argument '{k}' expected '{expected_type.__name__}' but got '{type(reqjson[k]).__name__}'")


def check_request_json(expected: Dict[str, type]):
    def wrapper(endpoint_func):
        def wrapped(*args, **kwargs):
            try:
                check_json(expected, request.json)
            except RequestJsonError as e:
                return f"Invalid Request: {e.args[0]}", 400

            return endpoint_func(*args, **kwargs)


        wrapped.__name__ = endpoint_func.__name__
        wrapped.__doc__ = endpoint_func.__doc__
        return wrapped

    return wrapper
