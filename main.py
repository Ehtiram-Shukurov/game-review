import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from functools import wraps
from db import *
from igdbAPI import *
from post import *
import threading
from datetime import datetime
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

@app.context_processor
def inject_user_sub():
    user_info = session.get("user")
    user_sub = user_info.get("user_sub") if user_info else None
    return {"user_sub": user_sub}  # Make user_sub available in all templates


@app.template_filter('format_date')
def format_date(value):
    try:
        # Convert to integer if the value is a string
        timestamp = int(value)
        return datetime.fromtimestamp(timestamp).strftime('%d %b %Y')
    except (ValueError, TypeError):
        # Return a fallback message in case of conversion issues
        return "Unknown"


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
        # Redirect to Login page here or maybe something else
            return redirect("/login")
        return f(*args, **kwargs) #do the normal behavior -- return as it does.

    return decorated

#TODO: add redirect page to see what the user wants to do if they try to access a forbidden page


@app.route('/postReview/<int:gameid>')
@requires_auth
def post_review(gameid):
    return render_template('postReview.html', game_id=gameid,user = session.get('user'))


@app.route('/postTopic/<int:gameid>')
@requires_auth
def post_topic(gameid):
    return render_template('postTopic.html', game_id=gameid, user = session.get('user'))


@app.route('/submitPost', methods=['POST'])
@requires_auth
def submit_post():
    if request.method == 'POST':
        title = request.form['title']
        game_id = request.form['game_id']
        content = request.form['content']
        post_type = request.form['post_type']
        
        rating = None
        if post_type == 'review': rating = request.form['rating']
        
        user_id = get_user_by_sub(session.get('user').get('user_sub'))['user_id']
        parent_id = None

        save_game_by_game_id(game_id)

        insert_post(title, game_id, content, post_type, rating, user_id, parent_id)
        post_id = get_user_most_recent_post(user_id)['post_id']

        return redirect(url_for('template_review_page', id=post_id))


@app.route('/editReview/<string:id>', methods=['GET'])
@requires_auth
def edit_review(id):
    post = get_post_by_id(id)
    post_data = {
        'id': post['post_id'],
        'title': post['title'],
        'content': post['content']
    }
    return render_template('editReview.html', post=post_data, user = session.get('user'))


@app.route('/editTopic/<string:id>', methods=['GET'])
@requires_auth
def edit_topic(id):
    post = get_post_by_id(id)
    post_data = {
        'id': post['post_id'],
        'title': post['title'],
        'content': post['content']
    }
    return render_template('editTopic.html', post=post_data, user=session.get('user'))



@app.route('/updatePost', methods=['POST'])
@requires_auth
def update_post():
    if request.method == 'POST':
        post_id = request.form['post_id']
        title = request.form['title']
        content = request.form['content']
        post_type = request.form['post_type']

        rating = None
        if post_type == 'review': rating = request.form['rating']

        update_post_db(title, content, rating, post_id)

        return redirect(url_for('template_review_page', id=post_id, user=session.get('user')))


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()

    user_info = token.get('userinfo', token)
    user_sub = user_info.get("sub")
    username = user_info.get("name", "")  
    email = user_info.get("email", "")  

    if not user_sub:
        return "User ID is missing", 400

    if not retrieve_user(user_sub):
        return redirect(url_for("complete_profile", user=session.get('user')))

    return redirect("/")


@app.route("/complete_profile", methods=["GET", "POST"])
def complete_profile():
    if request.method == "POST":
        user_data = {
            "user_sub": session["user"]["user_sub"],
            "username": request.form.get("username"),
            "email":session["user"]["email"],
            "descript": request.form.get("descript"),
            "profile_image_path": request.form.get("profile_image_path")
        }
        insert_user(user_data)

        return redirect(url_for("user_profile", user_sub=session.get('user').get('user_sub'), user=session.get('user')))

    return render_template("complete_profile.html")


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


@app.route("/")
def home():
    new_games = get_recent_games(limit=10)

    recent_reviews = []
    game_names = ["The Last of Us", "Cyberpunk 2077", "God of War"]  #TODO; Replace with dynamic data

    for name in game_names:
        review_data = get_game_data(name)
        if review_data:
            recent_reviews.append(review_data)
    print(session.get('user'))
    return render_template('home.html',new_games=new_games, recent_reviews=recent_reviews, user=session.get('user'))


@app.route("/user/profile")
@requires_auth
def user_profile():
    profile_info = retrieve_user(session.get('user').get('user_sub'))
    if not profile_info:
        return "User not found", 404
    return render_template("user_profile.html",user=session.get('user'), profile_info=profile_info,
                           active_page='profile')


@app.route('/user/reviews')
@requires_auth
#TODO: not sure if we should be sending user sub like this
def user_reviews():
    return render_template('user_reviews.html',user=session.get('user'), active_page='reviews')



@app.route('/user/settings', methods=['GET', 'POST'])
@requires_auth
def user_settings():
    user_sub = session.get('user').get('user_sub')
    profile_info = retrieve_user(user_sub)
    if not profile_info:
        return "User not found", 404

    if request.method == 'POST':
        new_username = request.form.get('new-username')
        new_email = request.form.get('new-email')
        descript = request.form.get('descript')

        update_user_profile(user_sub, new_username, new_email, descript)
        profile_info = retrieve_user(user_sub)

    return render_template("user_settings.html", user=session.get('user'), profile_info=profile_info,
                           active_page='settings')



@app.route('/review/<string:id>')
def template_review_page(id):
    review = retrieve_review_by_post_id(id)

    replies_data = retrieve_replies_by_post_id(id)
    # recursively put replies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    if replies:
     review['replies'] = replies
    return render_template("review.html", review=review, user=session.get('user'))


@app.route('/game/<string:id>')
def template_game_page(id):
    game_data = get_game_by_id(id)[0]
    reviews = retrieve_reviews_by_game_id(id)
    topics = retrieve_topics_by_game_id(id)
    valid = game_data.get('cover')
    # no cover image check
    if valid is None or valid.get("url") is None:
        valid = False
    else:
        valid = True
    return render_template("game.html", game_data=game_data, reviews=reviews, topics=topics, user=session.get('user'),valid= valid)


@app.route('/games')
def games_page():
    def get_games(genre):
        games = get_games_by_genre(genre)
        thread = threading.Thread(target = save_games_by_game_data, args = (games,))
        thread.start()
        return games
    return render_template("games.html", games=get_games, user=session.get('user'))

@app.route('/updateReply/<int:parent_id>/<int:post_id>', methods=['POST'])
@requires_auth
def update_reply(parent_id, post_id):
    data = request.form
    update_data = {
        'post_id': post_id,
        'content': data['editArea']
    }
    update_reply_content(update_data)
    return redirect(url_for('template_review_page', id=parent_id))


@app.route('/reply/<int:parent_id>', methods=['POST'])
def reply(parent_id):
    #todo: can we pass parent id in the form?
    data = request.form
    id = retrieve_user_id_by_sub(session.get('user').get('user_sub'))['user_id']
    insert_post(None, None, data['reply'], 'reply', None, id,parent_id)
    return redirect(url_for('template_review_page', id=parent_id))


@app.route('/inlineReply/<int:review_id>/<int:parent_id>', methods=['POST'])
@requires_auth
def inline_reply(review_id, parent_id):
    data = request.form
    id = retrieve_user_id_by_sub(session.get('user').get('userinfo').get('sub'))['user_id']
    insert_post(None, None, data['reply'], 'reply', None, id, parent_id)
    return redirect(url_for('template_review_page', id=review_id))

@app.route('/results', methods=['POST'])
def results():
    filter = request.form.get("searchOption")
    query = request.form.get('query')
    if filter =="Topic":
        results=retrieve_all_post("topic",query)
    if filter =="Game":
        data = broad_search(query)
        results={}
        for d in data:
            results[d["id"]] =d["name"]
    if filter =="Review":
        results=retrieve_all_post("review",query)
        #TODO: IDK THIS is a mess
    return render_template("results.html",results=results,filter=filter)

#TODO: IDK IF WE NEED FILTERS
@app.route('/redirects', methods=['POST'])
def redirects():
    filter = request.form.get("filter")
    id = request.form.get("selectedResult")
    if filter =="Topic":
        #TODO: does not look like we have one for topic
        pass
    if filter =="Game":
        return redirect(url_for('template_game_page', id=id))
    if filter =="Review":
        return redirect(url_for('template_review_page', id=id))

@app.route('/deletePost/<int:post_id>/<int:delete_id>')
@requires_auth
def delete_post(post_id, delete_id):
    delete_content(delete_id)
    if post_id == delete_id:
        return redirect(url_for('home'))
    
    return redirect(url_for('template_review_page', id=post_id))
