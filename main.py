import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from functools import wraps
from db import *
from igdbAPI import *
import psycopg2

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

@app.route('/postReview')
def postReview():
    games = ["game1", "game2", "game3"]
    return render_template('postReview.html', listGames=games)

@app.route('/postTopic')
def postTopic():
    games = ["game1", "game2", "game3"]
    return render_template('postReview.html', listGames=games)

@app.route('/submitPost', methods=['POST'])
def submitPost():
    if request.method == 'POST':
        title = request.form['title']
        game_id = request.form['game']
        content = request.form['content']
        post_type = request.form['post_type']
        
        rating = None
        if post_type == 'review': rating = request.form['rating']
        
        user_id = session.get('user')
        parent_id = -1
        dt = datetime.now()

        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()

        cur.execute("INSERT INTO POSTS (game_id, title, created, rating, content, post, parent_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", 
                    (game_id, title, dt, rating, content, post_type, parent_id, user_id))

        conn.commit()
        conn.close()

        post_id = get_user_most_recent_post(user_id)
        
        #discuss possible endpoint change
        return redirect(url_for('review', id=post_id))

@app.route('/updateReview/<string:id>', methods=['GET'])
def updateReview(id):
    post = getPost(id)
    post_data = {
        'id': post[0],
        'title': post[2],
        'content': post[5]
    }
    return render_template('updateReview.html', post=post_data)

@app.route('/updateTopic/<string:id>', methods=['GET'])
def updateTopic(id):
    post = getPost(id)
    post_data = {
        'id': post[0],
        'title': post[2],
        'content': post[5]
    }
    return render_template('updateTopic.html', post=post_data)

@app.route('/updatePost')
def updatePost():
    if request.method == 'POST':
        post_id = request.form['post_id']
        title = request.form['title']
        content = request.form['content']
        post_type = request.form['post_type']

        rating = None
        if post_type == 'review': rating = request.form['rating']

        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()

        cur.execute("UPDATE POSTS SET title = %s, content = %s, rating = %s, WHERE id = %s", (title, content, rating, post_id))

        conn.commit()
        conn.close()

    #discuss possible endpoint change
    return redirect(url_for('review', id=post_id))

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


@app.route('/review/<string:id>')
@auth_aware # <---- adding this makes the user to view the end point
#@requires_auth <---- adding this makes the user not able to see the end point unless they are logged in
def template_review_page(id, user):
    if user == None: # <--- do logic here for allowing the user to post,edit,delete, etc..
        pass
    # TODO: get real data from database
    reply = {"author": "Fred",
             "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
             "replies": []}
    comments = [{"author": "dano",
                 "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
                 "replies": [reply]}, {"author": "dano",
                                       "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Lorem ipsum dolor si",
                                       "replies": [reply]}]
    review = {"author": "danb", "gametitle": "test game", "title": "review page", "rating": '5', "comments": comments}
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

def get_user_most_recent_post(user_id):
    resultArr = []

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute("SELECT row_to_json(r) FROM POSTS as r WHERE user_id = %s ORDER BY created DESC;", (user_id))
    resultArr.extend(record for record in cur)

    conn.commit()
    conn.close()

    return resultArr[0][0]['post_id']

def getPost(id):
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute("SELECT * FROM POSTS WHERE post_id = %s", (id))
    post = cur.fetchone()

    conn.commit()
    conn.close()

    return post
