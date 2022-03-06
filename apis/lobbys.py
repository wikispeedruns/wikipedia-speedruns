from flask import jsonify, request, Blueprint, session

import json

from util.decorators import check_json, check_user, check_request_json, OptionalArg

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


@lobby_api.post("/<lobby_id:int>/prompts")
@check_user()
@check_request_json({"start": str, "end": str})
def add_lobby_prompts(lobby_id):
    user_id = session.get("user_id")
    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)

    if user_info is None or not user_info["owner"]:
        return "Only the owner can add prompts to this lobby", 401

    start = request.json["start"]
    end = request.json["end"]

    lobbys.add_lobby_prompt(lobby_id, start, end)
    return "Prompt Added!", 200


# TODO allow anonymous users?
@lobby_api.get("/<lobby_id:int>/prompts")
def get_lobby_prompts(lobby_id):
    user_id = session.get("user_id")

    if not (lobby_id in session["groups"]
            or lobbys.get_lobby_user_info(lobby_id, user_id)):
        return "You are not a member of this lobby", 401

    return jsonify(lobbys.get_lobby_prompts(lobby_id))
