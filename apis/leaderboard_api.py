from dis import show_code
from lib2to3.pgen2.token import OP
import re
from flask import Flask, jsonify, request, Blueprint, session
from itsdangerous import json

from util.decorators import check_request_json, OptionalArg

from wikispeedruns import leaderboards, lobbys, prompts

leaderboard_api = Blueprint('leaderboards', __name__, url_prefix='/api')

LEADERBOARD_JSON = {
    field: OptionalArg(basetype)
    for field, basetype in {
        "offset": int,
        "limit": int,

        "user_id": int,

        "played_before": int,
        "played_after": int,
        "show_unfinished": bool,
        "show_anonymous": bool,

        "user_run_mode": str,

        "sort_mode": str,
        "sort_asc": bool,
    }.items()
}


@leaderboard_api.post('/sprints/<int:prompt_id>/leaderboard', defaults={'run_id' : None})
@leaderboard_api.post('/sprints/<int:prompt_id>/leaderboard/<int:run_id>')
@check_request_json(LEADERBOARD_JSON)
def get_sprint_leaderboard(prompt_id, run_id):
    resp = leaderboards.get_leaderboard_runs(
        prompt_id=prompt_id,
        run_id=run_id,
        **request.json
    )

    resp["prompt"] = prompts.get_prompt(prompt_id=prompt_id, prompt_type="sprint")

    return jsonify(resp), 200


@leaderboard_api.post('/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/leaderboard', defaults={'run_id' : None})
@leaderboard_api.post('/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/leaderboard/<int:run_id>')
@check_request_json(LEADERBOARD_JSON)
def get_lobby_leaderboard(lobby_id, prompt_id, run_id):
    if not lobbys.check_leaderboard_access(lobby_id, prompt_id, session):
        return "Leaderboard locked! Play the prompt to view", 401

    resp = leaderboards.get_leaderboard_runs(
        lobby_id=lobby_id,
        prompt_id=prompt_id,
        run_id=run_id,
        **request.json
    )

    prompts = lobbys.get_lobby_prompts(lobby_id=lobby_id, prompt_id=prompt_id)
    if len(prompts) == 0:
        return f"Prompt {prompt_id} not found for lobby {lobby_id}", 404
    resp["prompt"] = prompts[0]
    return jsonify(resp), 200


@leaderboard_api.post('/sprints/<int:prompt_id>/stats', defaults={'run_id' : None})
@leaderboard_api.post('/sprints/<int:prompt_id>/stats/<int:run_id>')
@check_request_json(LEADERBOARD_JSON)
def get_sprint_leaderboard_stats(prompt_id, run_id):
    resp = leaderboards.get_leaderboard_stats(
        prompt_id=prompt_id,
        run_id=run_id,
        **request.json
    )

    return jsonify(resp), 200

@leaderboard_api.post('/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/stats', defaults={'run_id' : None})
@leaderboard_api.post('/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/stats/<int:run_id>')
@check_request_json(LEADERBOARD_JSON)
def get_lobby_leaderboard_stats(lobby_id, prompt_id, run_id):
    resp = leaderboards.get_leaderboard_stats(
        lobby_id=lobby_id,
        prompt_id=prompt_id,
        run_id=run_id,
        **request.json
    )

    return jsonify(resp), 200