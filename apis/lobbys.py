from flask import jsonify, request, Blueprint, session

import json

from util.decorators import check_user, check_request_json, OptionalArg

from wikispeedruns import lobbys

lobby_api = Blueprint('lobbys', __name__, url_prefix='/api/lobbys')

# TODO allow anonymous users?
@lobby_api.post("")
@check_user
@check_request_json({
    "name": OptionalArg(str),
    "desc": OptionalArg(str),
    "rules": dict
})
def create_lobby():
    user_id = session["user_id"]

    name = request.json.get("name")
    desc = request.json.get("desc")
    rules = json.dumps(request.json.get("rules"))

    lobby_id = lobbys.create_lobby(user_id, rules, name, desc)
    return jsonify({
        "lobby_id": lobby_id
    })
