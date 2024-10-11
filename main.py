import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
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

@app.route("/")
def home():
    return render_template('home.html', user_logged_in='user1')  # user_logged_in is just for testing the navbar


@app.route('/user/profile')
def user_profile():
    return render_template('user_profile.html', active_page='profile')


@app.route('/user/reviews')
def user_reviews():
    return render_template('user_reviews.html', active_page='reviews')


@app.route('/user/settings')
def user_settings():
    return render_template('user_settings.html', active_page='settings')


# Controllers API
 #TODO change home page to the following
# below is the code from the example downloaded from auth0
#@app.route("/a")
#def home():
#   return render_template(
#       "home.html",
#       session=session.get("user"),
#       pretty=json.dumps(session.get("user"), indent=4),
#   )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
        # Redirect to Login page here or maybe something else
            redirect("/login")
        return f(*args, **kwargs) #do the normal behavior -- return as it does.

    return decorated

# code written by Proffesor
def auth_aware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get('user')
        return f(*args, user=user, **kwargs) #do the normal behavior -- return as it does.

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

@auth_aware # <---- adding this makes the user to view the end point
@app.route('/review/<string:id>/<string:user>')
def template_review_page(id, user):
    if user == None: # <--- do logic here for allowing the user to post,edit,delete, etc..
        pass
      
    result = retrieve_review_by_post_id(id)
    print(result)
    replies_data = retrive_replies_by_post_id(id)
   
    # recursively put relies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    review = {"post_id":result['post_id'],"author": result['username'], "gametitle": result['game_id'], "title": result['title'], "rating": result['rating'], "content": result['content'], "replies": replies}

    return render_template("review.html", review=review)


@app.route('/game/<string:name>')
#@auth_aware # <---- adding this makes the user to view the end point
#@requires_auth <---- adding this makes the user not able to see the end point unless they are logged in
def template_game_page(name):
    game_data = get_game_data(name)
    reviews = retrieve_reviews_by_game_id(game_data['game_id'])
    topics = retrieve_topics_by_game_id(game_data['game_id'])
    return render_template("game.html", game_data=game_data, reviews=reviews, topics=topics)


@app.route('/updateReview/<int:post_id>', methods=['POST'])
def update_review(post_id):
    data = request.form
    print(data)
    update_data = {
        'post_id': post_id,
        'title': data['title'],
        'rating': data['rating'],
        'content': data['editArea']
    }
    update_reviews(update_data)
    return redirect(url_for('template_review_page', id=post_id, user='user1'))
    
@app.route('/editReview/<string:id>')
def edit_review(id):
    result = retrieve_review_by_post_id(id)
    print(result)
    return render_template('editReview.html', result = result)

@app.route('/updateReply/<int:parent_id>/<int:post_id>', methods=['POST'])
def update_reply(parent_id, post_id):
    data = request.form
    print(data)
    update_data = {
        'post_id': post_id,
        'content': data['editArea']
    }
    update_reply_content(update_data)
    return redirect(url_for('template_review_page', id=parent_id, user='user1'))