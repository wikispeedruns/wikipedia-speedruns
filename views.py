from flask import Blueprint, render_template, request, redirect, session

from util.decorators import check_admin, check_user

import db
import random

import wikispeedruns

views = Blueprint("views", __name__)

# Passes session args to function if needed
def render_with_data(template, **kwargs):

    data = kwargs

    if ("user_id" in session):
        data["user_id"] = session["user_id"]
        data["username"] = session["username"]

    # only use for rendering non-data front-end UI elements
    if "admin" in session and session["admin"]:
        data["admin"] = True

    return render_template(template, data=data)

# Front end pages
@views.route('/', methods=['GET'])
def get_home_page():
    return render_with_data('home.html')

@views.route('/about', methods=['GET'])
def get_about_page():
    return render_with_data('about.html')


@views.route('/archive', methods=['GET'])
def get_archive_page():
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        return render_with_data('archive.html', limit=limit, offset=offset)
    except ValueError:
        return "Page Not Found", 404

@views.route('/random', methods=['GET'])
def get_random_prompt():
    query = ("""
    SELECT prompt_id
    FROM sprint_prompts
    WHERE used = 1 AND active_end <= NOW();
    """)

    with db.get_db().cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        rand_prompt = random.choice(results)[0]
        return redirect("/play/" + str(rand_prompt), code=302)

@views.route('/register', methods=['GET'])
def get_register_page():
    return render_with_data('users/register.html')


@views.route('/pending', methods=['GET'])
def get_create_oauth_account_page():
    if ("pending_oauth_creation" in session):
        return render_with_data('users/pending.html')
    else:
        return redirect('/')

@views.route('/login', methods=['GET'])
def get_login_page():
    return render_with_data('users/login.html')

@views.route('/profile/<username>', methods = ['GET'])
def get_profile_page(username):
    return render_with_data('profile.html', profile_name=username)

@views.route('/reset/request', methods=['GET'])
def get_reset_request_page():
    return render_with_data('users/reset_password_request.html')

@views.route('/reset/<id>/<token>', methods=['GET'])
def get_reset_page(id, token):
    return render_with_data('users/reset_password.html', id=id, token=token)

@views.route('/confirm/<token>', methods=['GET'])
def get_confirm_page(token):
    return render_with_data('users/confirm_email.html', token=token)

# sprint pages
@views.route('/play/tutorial', methods=['GET'])
def get_tutorial_page():
    return render_with_data('tutorial.html')

@views.route('/play/<int:id>', methods=['GET'])
def get_sprint_play_page(id):
    return render_with_data('play.html', prompt_id=id)

@views.route('/lobby/<int:lobby_id>/play/<int:prompt_id>', methods=['GET'])
def get_lobby_play_page(lobby_id, prompt_id):
    return render_with_data('play.html', lobby_id=lobby_id, prompt_id=prompt_id)

@views.route('/play/quick_play', methods=['GET'])
def get_quick_run_page():
    try:
        prompt_start = request.args.get('prompt_start', None)
        prompt_end = request.args.get('prompt_end', None)
        scroll = request.args.get('scroll', None)
        lang = request.args.get('lang', 'en')
        if prompt_start is None or prompt_end is None or not lang.strip():
            return "Invalid request", 400
        return render_with_data('play.html', prompt_start=prompt_start, prompt_end=prompt_end, scroll=scroll, lang=lang)
    except ValueError:
        return "Page Not Found", 404

# leaderboard(s)
@views.route('/leaderboard/<prompt_id>', methods=['GET'])
def get_leaderboard_page(prompt_id):
    return render_with_data('leaderboard.html', prompt_id=prompt_id)

@views.route('/lobby/<int:lobby_id>/leaderboard/<int:prompt_id>', methods=['GET'])
def get_lobby_leaderboard_page(lobby_id, prompt_id):
    return render_with_data('leaderboard.html', prompt_id=prompt_id, lobby_id=lobby_id)

@views.route('/replay', methods=['GET'])
def get_replay_page():
    run_id = request.args.get('run_id', '')
    return render_with_data('replay.html', run_id=run_id)

@views.route('/account', methods=['GET'])
def get_user_account_page():
    return render_with_data('account.html')

# Finish pages
@views.route('/finish', methods=['GET'])
def get_sprint_finish_page():
    try:
        run_id = int(request.args.get('run_id', -1))
        played = request.args.get('played', False)
        return render_with_data('play_finish.html', type='sprint', run_id=run_id, played=played)
    except ValueError:
        return "Page Not Found", 404

@views.route('/lobby/<int:lobby_id>/finish', methods=['GET'])
def get_lobby_finish_page(lobby_id):
    try:
        run_id = int(request.args.get('run_id', -1))
        played = request.args.get('played', False)
        return render_with_data('play_finish.html', type='lobby', run_id=run_id, lobby_id=lobby_id, played=played)
    except ValueError:
        return "Page Not Found", 404

@views.route('/quick_run/finish', methods=['GET'])
def get_quick_finish_page():
    try:
        run_id = int(request.args.get('run_id', -1))
        played = request.args.get('played', False)
        return render_with_data('play_finish.html', type='quick', run_id=run_id, played=played)
    except ValueError:
        return "Page Not Found", 404

# Marathon pages
@views.route('/play/marathon/<id>', methods=['GET'])
def get_marathon_play_page(id):
    loadsave = request.args.get('load_save', 0)
    print(loadsave)
    return render_with_data('marathon.html', prompt_id=id, load_save=loadsave)

@views.route('/marathonruns/<username>', methods=['GET'])
def get_marathon_personal_leaderboard(username):
    page = request.args.get('page', 1)
    sortMode = request.args.get('sort', 'cp')
    return render_with_data('marathon_prompt.html', pg = page, sortMode=sortMode, profile_name=username)

# Lobby Pages
@views.route('/lobby/create', methods=['GET'])
@check_user
def get_lobby_create_page():
    return render_with_data('lobbys/create.html', )


@views.route('/lobby/<int:lobby_id>', methods=['GET'])
def get_lobby_page(lobby_id):
    if wikispeedruns.lobbys.check_membership(lobby_id, session):
        return render_with_data('lobbys/lobby.html', lobby_id=lobby_id)
    else:
        return render_with_data('lobbys/join.html', lobby_id=lobby_id)


# Generator
@views.route('/generator', methods=['GET'])
def get_generator_page():
    return render_with_data('generator.html')


# Admin pages
@views.route('/manage', methods=['GET'])
@check_admin
def get_manage_page():
    return render_with_data('admin/manage.html')

@views.route('/testarticle', methods=['GET'])
@check_admin
def get_test_article_page():
    return render_with_data('admin/articleTester.html')

@views.route('/stats', methods=['GET'])
@check_admin
def get_stats_page():
    return render_with_data('admin/stats.html')


@views.route('/labeler', methods=['GET'])
def get_labeler_page():
    return render_with_data('admin/categoryLabeler.html')


@views.route('/devblog', methods=['GET'])
def get_devblog_page():
    return render_with_data('devblog/blog.html')


# Error pages
@views.route('/error', methods=['GET'])
def get_gen_error_page():
    return render_with_data('users/generic_error.html')

