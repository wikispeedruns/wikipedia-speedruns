from tracemalloc import start
from flask import jsonify, request, Blueprint, session

import json
import datetime

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


@lobby_api.post("/<int:lobby_id>/join")
@check_request_json({"passcode": str, "name": OptionalArg(str)})
def join_lobby(lobby_id):

    lobby = lobbys.get_lobby(lobby_id)

    passcode = request.json["passcode"]

    if lobby is None:
        return f"Lobby {lobby_id} not found", 404

    if lobby["passcode"] != passcode:
        return f"Incorrect passcode", 401

    if ("user_id" in session):
        user_id = session["user_id"]
        if not (lobbys.join_lobby_as_user(lobby_id, user_id)):
            return f"Unknown error joining lobby {lobby_id}", 500

    else:
        if "name" not in request.json:
            return "Invalid request", 400

        name = request.json["name"]

        if ("lobbys" not in session):
            session["lobbys"] = {}
        session["lobbys"][lobby_id] = name

    return "Joined lobby", 200



@lobby_api.get("/<int:lobby_id>")
def get_lobby(lobby_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401



    lobby_info = lobbys.get_lobby(lobby_id)
    if lobby_info is None:
        return "Lobby does not exist", 404

    # fill out user info
    lobby_user_info = {}
    if "user_id" in session:
        lobby_user_info["name"] = session["username"]
        lobby_user_info["owner"] = lobbys.get_lobby_user_info(lobby_id, session["user_id"]).get("owner", False)
    else:
        lobby_user_info["name"] = session["lobbys"][str(lobby_id)]
        lobby_user_info["owner"] = False

    lobby_info["user"] = lobby_user_info

    return lobby_info


# Prompts

@lobby_api.post("/<int:lobby_id>/prompts")
@check_user
@check_request_json({"start": str, "end": str})
def add_lobby_prompt(lobby_id):
    user_id = session.get("user_id")
    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)

    if user_info is None or not user_info["owner"]:
        return "Only the owner can add prompts to this lobby", 401

    start = request.json["start"]
    end = request.json["end"]

    lobbys.add_lobby_prompt(lobby_id, start, end)
    return "Prompt Added!", 200


# TODO allow anonymous users?
@lobby_api.get('/<int:lobby_id>/prompts', defaults={'prompt_id' : None})
@lobby_api.get("/<int:lobby_id>/prompts/<int:prompt_id>")
def get_lobby_prompts(lobby_id, prompt_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You are not a member of this lobby", 401

    prompts = lobbys.get_lobby_prompts(lobby_id, prompt_id)

    if prompt_id is None:
        return jsonify(prompts)
    else:
        if len(prompts) == 0:
            return "Prompt not found", 404

        return jsonify(prompts[0])




# Runs
@lobby_api.post("/<int:lobby_id>/prompts/<int:prompt_id>/runs")
@check_request_json({"start_time": int, "end_time": int, "path": list})
def add_lobby_run(lobby_id, prompt_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    run_id = lobbys.add_lobby_run(
        lobby_id   = lobby_id,
        prompt_id  = prompt_id,
        start_time = datetime.datetime.fromtimestamp(request.json['start_time']/1000),
        end_time   = datetime.datetime.fromtimestamp(request.json['end_time']/1000),
        path       = json.dumps(request.json['path']),
        user_id    = session.get("user_id"),
        name       = session.get("lobbys", {}).get(str(lobby_id))
    )

    return jsonify({"run_id": run_id})

# Runs
@lobby_api.get("/<int:lobby_id>/prompts/<int:prompt_id>/runs")
def get_lobby_runs(lobby_id, prompt_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    runs = lobbys.get_lobby_runs(lobby_id, prompt_id)

    return jsonify(runs), 200