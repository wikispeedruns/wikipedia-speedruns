from flask import Blueprint, render_template, request, redirect, session

from util.decorators import check_admin

import db
import random

views = Blueprint("views", __name__)

# Passes session args to function if needed
def render_with_data(template, **kwargs):

    data = kwargs

    if ("user_id" in session):
        data["user_id"] = session["user_id"]
        data["username"] = session["username"]

        return render_template(template, data=data)
    else:
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


@views.route('/prompt/<id>', methods=['GET'])
def get_prompt_page(id):
    run_id = request.args.get('run_id', '')
    page = request.args.get('page', 1)
    sortMode = request.args.get('sort', 'time')

    if int(page) < 1:
        page = 1

    if len(run_id) != 0:
        return render_with_data('prompt.html', prompt_id=id, run_id=run_id, pg = page, sortMode=sortMode)
    else:
        return render_with_data('prompt.html', prompt_id=id, pg = page, sortMode=sortMode)


@views.route('/play/<id>', methods=['GET'])
def get_play_page(id):
    return render_with_data('play.html', prompt_id=id)

@views.route('/confirm/<token>', methods=['GET'])
def get_confirm_page(token):
    return render_with_data('users/confirm_email.html', token=token)

@views.route('/reset/request', methods=['GET'])
def get_reset_request_page():
    return render_with_data('users/reset_password_request.html')

@views.route('/reset/<id>/<token>', methods=['GET'])
def get_reset_page(id, token):
    return render_with_data('users/reset_password.html', id=id, token=token)

@views.route('/error', methods=['GET'])
def get_gen_error_page():
    return render_with_data('users/generic_error.html')


# Admin pages


@views.route('/manage', methods=['GET'])
@check_admin
def get_manage_page():
    return render_with_data('admin/manage.html')

@views.route('/testarticle', methods=['GET'])
@check_admin
def get_test_article_page():
    return render_with_data('admin/articleTester.html')
