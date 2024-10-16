import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, request
from functools import wraps
from db import *
from igdbAPI import *
from post import *

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)

setup()

app.secret_key = os.environ['AUTH0_SECRET_KEY']

oauth = OAuth(app)
domain = os.environ['AUTH0_DOMAIN']
oauth.register(
    "auth0",
    client_id=os.environ['AUTH0_CLIENT_ID'],
    client_secret=os.environ['AUTH0_SECRET'],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{domain}/.well-known/openid-configuration',
)

# code written by Proffesor
def auth_aware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get('user')
        return f(*args, user=user, **kwargs) #do the normal behavior -- return as it does.
    return decorated


@app.route("/")
def home():
    return render_template('home.html', user_logged_in=session.get('user'))  # user_logged_in is just for testing the navbar


@app.route('/user/profile')
def user_profile():
    return render_template('user_profile.html', active_page='profile')


@app.route('/user/reviews')
def user_reviews():
    return render_template('user_reviews.html', active_page='reviews')


@app.route('/user/settings')
def user_settings():
    return render_template('user_settings.html', active_page='settings')


@app.route('/postReview')
def post_review():
    games = ["game1", "game2", "game3"]
    return render_template('postReview.html', listGames=games)


@app.route('/postTopic')
def post_topic():
    games = ["game1", "game2", "game3"]
    return render_template('postReview.html', listGames=games)


@app.route('/submitPost', methods=['POST'])
def submit_post():
    if request.method == 'POST':
        title = request.form['title']
        game_id = request.form['game']
        content = request.form['content']
        post_type = request.form['post_type']
        
        rating = None
        if post_type == 'review': rating = request.form['rating']
        
        user_id = session.get('user')
        parent_id = None

        insert_post(title, game_id, content, post_type, rating, user_id, parent_id)

        post_id = get_user_most_recent_post(user_id)
        
        #discuss possible endpoint change
        return redirect(url_for('review', id=post_id))


@app.route('/editReview/<string:id>', methods=['GET'])
def update_review(id):
    post = get_post_by_id(id)
    post_data = {
        'id': post['post_id'],
        'title': post['title'],
        'content': post['content']
    }
    return render_template('editReview.html', post=post_data)


@app.route('/editTopic/<string:id>', methods=['GET'])
def update_topic(id):
    post = get_post_by_id(id)
    post_data = {
        'id': post['post_id'],
        'title': post['title'],
        'content': post['content']
    }
    return render_template('editTopic.html', post=post_data)

@app.route('/updatePost', methods=['POST'])
def update_post():
    if request.method == 'POST':
        print(request.form)
        post_id = request.form['post_id']
        title = request.form['title']
        content = request.form['content']
        post_type = request.form['post_type']

        rating = None
        if post_type == 'review': rating = request.form['rating']

        update_post_db(title, content, rating, post_id)

        return redirect(url_for('template_review_page', id=post_id, user='user1'))


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
        # Redirect to Login page here or maybe something else
            redirect("/login")
        return f(*args, **kwargs) #do the normal behavior -- return as it does.

    return decorated


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token

    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + domain
        + "/v2/logout?"
        + urlencode(
            {
                # replace hello_world with actual function for homepage endpoint

                "returnTo": url_for("home", _external=True),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        )
    )


@app.route('/review/<string:id>')
def template_review_page(id):
    review = retrieve_review_by_post_id(id)
    sub=session.get('user').get('userinfo').get('sub')
    replies_data = retrieve_replies_by_post_id(id)
    # recursively put replies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    review['replies'] = replies
    return render_template("review.html", review=review, sub=sub)


@auth_aware # <---- adding this makes the user to view the end point
@app.route('/game/<string:id>')
#@requires_auth <---- adding this makes the user not able to see the end point unless they are logged in
def template_game_page(id):
    game_data = get_game_by_id(id)[0]
    reviews = retrieve_reviews_by_game_id(id)
    topics = retrieve_topics_by_game_id(id)
    return render_template("game.html", game_data=game_data, reviews=reviews, topics=topics)


@app.route('/games')
def games_page():
    def get_games(genre):
        return get_games_by_genre(genre)
    return render_template("games.html", games=get_games)


@app.route('/updateReply/<int:parent_id>/<int:post_id>', methods=['POST'])
def update_reply(parent_id, post_id):
    data = request.form
    update_data = {
        'post_id': post_id,
        'content': data['editArea']
    }
    update_reply_content(update_data)
    return redirect(url_for('template_review_page', id=parent_id, user='user1'))

@app.route('/reply/<int:parent_id>', methods=['POST'])
def reply(parent_id):
    data = request.form
    id = retrieve_user_id_by_sub(session.get('user').get('userinfo').get('sub'))
    reply_data = {
        'title': None,
        'rating': None,
        'content': data['reply'],
        'post_type': 'reply',
        'parent_id': parent_id,
        'user_id': id['user_id']
    }
    insert_post(None, None, reply_data['content'], reply_data['post_type'], None, reply_data['user_id'], reply_data['parent_id'])
    return redirect(url_for('template_review_page', id=parent_id, user='user1'))
