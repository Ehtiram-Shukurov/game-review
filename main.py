import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from functools import wraps
from db import *
from igdbAPI import *

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
#@requires_auth <---- adding this makes the user not able to see the end point unless they are logged in
@app.route('/review/<string:id>')
def template_review_page(id, user):
    if user == None: # <--- do logic here for allowing the user to post,edit,delete, etc..
        pass
      
    result = retrieve_review_by_post_id(id)
    replies_data = retrive_replies_by_post_id(id)
   
    # recursively put relies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    review = {"author": result['username'], "gametitle": result['game_id'], "title": result['title'], "rating": result['rating'], "content": result['content'], "replies": replies}

    # TODO: get real data from database
    # reply = {"author": "Fred",
    #          "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
    #          "replies": []}
    # comments = [{"author": "dano",
    #              "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
    #              "replies": [reply]}, {"author": "dano",
    #                                    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
    #                                    "replies": [reply]}]
    # review = {"author": "danb", "gametitle": "test game", "title": "review page", "rating": '5', "comments": comments}
    # comments = review['comments'];  TOOD: figure out how to best get review/comment data from DB
    # TODO: replace the return with the html template with info from data
    # data.get("coverImageUrl")
    # data.get("gameModes")
    # data.get("genres")
    # data.get("companies")
    # data.get("playerPerspectives")
    # data.get("similarGames")
    # data.get("storyline")
    # data.get("summary")
    # data.get("themes")
    return render_template("review.html", review=review)


@app.route('/game/<string:name>')
@auth_aware # <---- adding this makes the user to view the end point
#@requires_auth <---- adding this makes the user not able to see the end point unless they are logged in
def template_game_page(name):
    game_data = get_game_data(name)
    reviews = retrieve_reviews_by_game_id(game_data['game_id'])
    topics = retrieve_topics_by_game_id(game_data['game_id'])
    return render_template("game.html", game_data=game_data, reviews=reviews, topics=topics)


def build_hierarchy(replies, parent_id=None):
    hierarchy = []
    for reply in replies:
        if reply['parent_id'] == int(parent_id):
            print('here')
            # Create a structure for the reply
            reply_structure = {
                'author': reply['username'],  # Using username for author
                'content': reply['content'],
                'replies': build_hierarchy(replies, reply['post_id'])  # Recursive call
            }
            hierarchy.append(reply_structure)
    return hierarchy