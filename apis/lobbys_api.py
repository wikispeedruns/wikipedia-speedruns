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
        session["lobbys"][str(lobby_id)] = name
        session.modified = True

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


@lobby_api.patch("/<int:lobby_id>")
@check_request_json({"rules": OptionalArg(dict), "name": OptionalArg(str), "desc": OptionalArg(str)})
def update_lobby(lobby_id):

    user_id = session.get("user_id")
    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)

    if user_info is None or not user_info["owner"]:
        return "Only the owner can add prompts to this lobby", 401

    rules = request.json.get("rules")
    name = request.json.get("name")
    desc = request.json.get("desc")

    lobbys.update_lobby(rules=rules, name=name, desc=desc)

    return "Updated lobby", 200

# Prompts
@lobby_api.post("/<int:lobby_id>/prompts")
@check_user
@check_request_json({"start": str, "end": str, "language": str})
def add_lobby_prompt(lobby_id):
    user_id = session.get("user_id")
    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)

    if user_info is None or not user_info["owner"]:
        return "Only the owner can add prompts to this lobby", 401

    start = request.json["start"]
    end = request.json["end"]
    language = request.json["language"]

    lobbys.add_lobby_prompt(lobby_id, start, end, language)
    return "Prompt Added!", 200


@lobby_api.get('/<int:lobby_id>/prompts', defaults={'prompt_id' : None})
@lobby_api.get("/<int:lobby_id>/prompts/<int:prompt_id>")
def get_lobby_prompts(lobby_id, prompt_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You are not a member of this lobby", 401

    prompts = lobbys.get_lobby_prompts(lobby_id, prompt_id, session)
    if prompt_id is None:
        # TODO base this on whether a prompt is played or not
        if not lobbys.check_prompt_end_visibility(lobby_id, session):
            prompts = [
                {
                    **p,
                    "end": p["end"] if p["played"] else None
                } for p in prompts
            ]
        return jsonify(prompts)
    else:
        if len(prompts) == 0:
            return "Prompt not found", 404

        return jsonify(prompts[0])


@lobby_api.delete("/<int:lobby_id>/prompts")
@check_user
@check_request_json({"prompts": list})
def delete_lobby_prompts(lobby_id):
    user_id = session.get("user_id")
    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)

    if user_info is None or not user_info["owner"]:
        return "Only the owner can delete prompts from this lobby", 401

    prompts = request.json["prompts"]

    lobbys.delete_lobby_prompts(lobby_id, prompts)
    return "Prompts Deleted!", 200


# Runs
@lobby_api.get("/<int:lobby_id>/prompts/<int:prompt_id>/runs")
def get_lobby_runs(lobby_id, prompt_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    runs = lobbys.get_lobby_runs(lobby_id, prompt_id)

    return jsonify(runs), 200


# Run
@lobby_api.get("/<int:lobby_id>/run/<int:run_id>")
def get_lobby_run(lobby_id, run_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    runs = lobbys.get_lobby_run(lobby_id, run_id)

    return jsonify(runs), 200


@lobby_api.get("/user_lobbys")
@check_user
def get_user_lobbies():

    user_id = session.get("user_id")
    lobbies = lobbys.get_user_lobbys(user_id)

    return jsonify(lobbies), 200


@lobby_api.get("/players/<int:lobby_id>")
@check_user
def get_lobby_users(lobby_id):

    user_id = session.get("user_id")

    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)
    if user_info is None or not user_info["owner"]:
        return "Only the host can check the list of lobby users", 401

    return jsonify(lobbys.get_lobby_users(lobby_id)), 200


@lobby_api.get("/anon_players/<int:lobby_id>")
@check_user
def get_lobby_anon_users(lobby_id):

    user_id = session.get("user_id")

    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)
    if user_info is None or not user_info["owner"]:
        return "Only the host can check the list of lobby users", 401

    return jsonify(lobbys.get_lobby_anon_users(lobby_id)), 200



@lobby_api.patch("/change_host/<int:lobby_id>")
@check_user
@check_request_json({"target_user_id": int})
def change_lobby_host(lobby_id):

    user_id = session.get("user_id")
    target_user_id = request.json["target_user_id"]

    user_info = lobbys.get_lobby_user_info(lobby_id, user_id)
    if user_info is None or not user_info["owner"]:
        return "Only the host can change host to another user", 401

    if user_id == target_user_id:
        return "User is already lobby host!", 400
    if not lobbys.check_user_membership(lobby_id, target_user_id):
        return "Target user is not a member of this lobby", 400

    lobbys.change_lobby_host(lobby_id, target_user_id)

    return "Lobby host changed successfully", 200