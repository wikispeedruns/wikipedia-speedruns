from flask import jsonify, request, Blueprint, session

import json

from util.decorators import check_json, check_user, check_request_json, OptionalArg

from wikispeedruns import lobbys

lobby_api = Blueprint('lobbys', __name__, url_prefix='/api/lobbys')


def _check_membership(lobby_id: int, session: dict) -> bool:
    user_id = session.get("user_id")
    if lobbys.get_lobby_user_info(lobby_id, user_id) is not None:
        return True

    # lobby_id gets converted to string in session when creating cookie apparently
    if "lobbys" in session and session["lobbys"].get(str(lobby_id)) is not None:
        return True

    return False


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


@lobby_api.post("/<int:lobby_id>/join")
def join_lobby(lobby_id):
    if ("user_id" in session):
        user_id = session["user_id"]

        if not (lobbys.join_lobby_as_user(lobby_id, user_id)):
            return f"Lobby {lobby_id} not found", 404

    else:
        if "passcode" not in request.json or "name" not in request.json:
            return "Invalid request", 400

        passcode = request.json["passcode"]
        name = request.json["name"]

        lobby = lobbys.get_lobby(lobby_id)

        if lobby is None:
            return f"Lobby {lobby_id} not found", 404

        if lobby["passcode"] != passcode:
            return f"Incorrect passcode", 401

        if ("lobbys" not in session):
            session["lobbys"] = {}

        session["lobbys"][lobby_id] = name

    return "Joined lobby", 200



@lobby_api.get("/<int:lobby_id>")
def get_lobby(lobby_id):
    print(lobby_id, session)
    if not _check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    ret = lobbys.get_lobby(lobby_id)
    if ret is None:
        return "Lobby does not exist", 404
    else:
        return ret


# Prompt management

@lobby_api.post("/<int:lobby_id>/prompts")
@check_user
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
@lobby_api.get("/<int:lobby_id>/prompts")
def get_lobby_prompts(lobby_id):
    if not _check_membership(lobby_id, session):
        return "You are not a member of this lobby", 401

    return jsonify(lobbys.get_lobby_prompts(lobby_id))
