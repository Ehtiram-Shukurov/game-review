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
def inject_user_info():
    user_info = session.get("user")
    user_sub = user_info.get("user_sub") if user_info else None
    if user_sub:
        picture = get_user_picture(user_sub)
    else:
        picture = None
    
    return {"user_sub": user_sub, "user_picture": picture}


@app.template_filter('format_date')
def format_date(value):
    try:
        timestamp = int(value)
        return datetime.fromtimestamp(timestamp).strftime('%d %b %Y')
    except (ValueError, TypeError):
        return "Unknown"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
        # Redirect to Login page here or maybe something else
            return redirect("/login")
        return f(*args, **kwargs) #do the normal behavior -- return as it does.
    return decorated

@app.errorhandler(Exception)
@app.route('/error')
def basic_error(e):
    print(e)
    message = str(e)
    return render_template("error.html",message =message)

@app.route('/postReview/<int:gameid>')
@requires_auth
def post_review(gameid):
    return render_template('postReview.html', game_id=gameid, user=session.get('user'))

@app.route('/postTopic/<int:gameid>')
@requires_auth
def post_topic(gameid):
    return render_template('postTopic.html', game_id=gameid, user=session.get('user'))

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

        if post_type == 'review':
            return redirect(url_for('template_review_page', id=post_id))
        return redirect(url_for('template_topic_page', id=post_id))


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

        if post_type == 'review':
            return redirect(url_for('template_review_page', id=post_id))
        
        return redirect(url_for('template_topic_page', id=post_id))


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()

    user_info = token.get('userinfo', token)
    user_sub = user_info.get("sub")
    username = user_info.get("name", "")  
    email = user_info.get("email", "")
    picture = user_info.get('picture', "")

    if not user_sub:
        return "User ID is missing", 400

    saved_user_info = retrieve_user(user_sub)

    if not saved_user_info:
        session["user"] = {
            "user_sub": user_sub,
            "username": username,
            "email": email,
            "picture": picture
        }
        return redirect(url_for("complete_profile"))

    session['user'] = saved_user_info
    return redirect("/")


@app.route("/complete_profile", methods=["GET", "POST"])
def complete_profile():
    user_sub = session["user"]["user_sub"]

    existing_user = retrieve_user(user_sub)
    if existing_user:
        return redirect(url_for("user_profile", user_id=existing_user["user_id"]))
    if request.method == "POST":
        user_data = {
            "user_sub": session["user"]["user_sub"],
            "username": request.form.get("username"),
            "email": session["user"]["email"],
            "descript": request.form.get("descript"),
            "picture": session["user"]['picture']
        }
        insert_user(user_data)
        user_id = retrieve_user_id_by_sub(session["user"]["user_sub"])['user_id']
        user_data['user_id'] = user_id
        session['user'] = user_data
        return redirect(url_for("user_profile", user_id=user_id))

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
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def home():
    new_games = get_recent_games(limit=10)
    recent_reviews = retrieve_recent_reviews(5)
    return render_template('home.html', new_games=new_games, recent_reviews=recent_reviews, user=session.get('user'))


@app.route('/user/id/<int:user_id>')
@requires_auth
def user_profile(user_id):
    current_user = retrieve_user(session.get('user').get('user_sub'))
    if current_user and current_user['user_id'] == user_id:
        review_count = count_reviews_by_user_id(user_id)
        return render_template("user_profile.html", review_count=review_count, user=session.get('user'), profile_info=current_user, is_own_profile=True, active_page='profile')
    else:
        profile_info = retrieve_user_by_id(user_id)
        if not profile_info:
            return "User not found", 404
        review_count = count_reviews_by_user_id(user_id)
        
        return render_template("user_profile.html", review_count=review_count, user=session.get('user'), profile_info=profile_info, is_own_profile=False, active_page='profile')


@app.route('/user/<int:user_id>/reviews')
def user_reviews(user_id):
    logged_in_user = retrieve_user(session.get('user').get('user_sub'))
    is_own_profile = False
    if logged_in_user and logged_in_user['user_id'] == user_id:
        is_own_profile = True
        profile_info = retrieve_user(logged_in_user['user_sub'])
    else:
        profile_info = retrieve_user_by_id(user_id)

    if not profile_info:
        return "User not found", 404

    reviews = retrieve_reviews_by_user_id(user_id)

    return render_template('user_reviews.html',profile_info=profile_info, user=session.get('user'), reviews=reviews, is_own_profile=is_own_profile, active_page='reviews')



@app.route('/user/settings', methods=['GET', 'POST'])
@requires_auth
def user_settings():
    user_sub = session.get('user').get('user_sub')
    profile_info = retrieve_user(user_sub)
    error_message = None
    success_message = None
    if not profile_info:
        return "User not found", 404

    if request.method == 'POST':
        new_username = request.form.get('new-username')
        new_email = request.form.get('new-email')
        descript = request.form.get('descript')
        picture = request.form.get('picture')
        if not new_username or not new_email:
            
            return "Username and email are required", 400

        if "@" not in new_email or "." not in new_email:
            return "Invalid email format", 400

        if not new_username or not new_email:
            error_message = "Username and email are required."
        elif "@" not in new_email or "." not in new_email:
            error_message = "Invalid email format."
        else:
            if picture:
                if picture != '':
                        update_user_profile_with_image(user_sub, new_username, new_email, descript, picture)
                        success_message = "Profile updated successfully."
                else:
                    update_user_profile(user_sub, new_username, new_email, descript)
                    success_message = "Profile updated successfully."
            else:
                update_user_profile(user_sub, new_username, new_email, descript)
                success_message = "Profile updated successfully."

        session['user'] = retrieve_user(user_sub)

    return render_template("user_settings.html", user=session.get('user'),
                           active_page='settings',error_message=error_message, 
        success_message=success_message)

@app.route("/delete_account", methods=["POST"])
@requires_auth 
def delete_account():
    user_sub = session.get('user').get('user_sub')
    user_info = retrieve_user(user_sub)
    
    if not user_info:
        return "User not found", 404
    user_id = user_info["user_id"]
    delete_user_account(user_id)
    return redirect(url_for('logout'))

@app.route('/review/<string:id>')
def template_review_page(id):
    review = retrieve_post_by_post_id(id,"review")
    replies_data = retrieve_replies_by_post_id(id)
    # recursively put replies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    game = get_game_by_id_database(review['game_id'])
    if replies:
        review['replies'] = replies
    return render_template("review.html", review=review, user=session.get('user'), game=game)

@app.route('/topic/<string:id>')
def template_topic_page(id):
    topic = retrieve_post_by_post_id(id,"topic")
    replies_data = retrieve_replies_by_post_id(id)
    # recursively put replies into hierarchy structure
    replies = build_hierarchy(replies_data,id)
    game = get_game_by_id_database(topic['game_id'])
    if replies:
        topic['replies'] = replies
    return render_template("topic.html", topic=topic, user=session.get('user'), game=game)

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

@app.route('/updateReply/<int:post_id>/<int:parent_id>', methods=['POST'])
@requires_auth
def update_reply(post_id, parent_id):
    data = request.form
    update_data = {
        'parent_id': parent_id,
        'content': data['editArea']
    }
    type = data['type']
    update_reply_content(update_data)
    if type == 'review':
        return redirect(url_for('template_review_page', id=post_id))
    return redirect(url_for('template_topic_page', id=post_id))


@app.route('/reply/<int:parent_id>', methods=['POST'])
@requires_auth
def reply(parent_id):
    #todo: can we pass parent id in the form?
    data = request.form
    type = data['type']
    id = retrieve_user_id_by_sub(session.get('user').get('user_sub'))['user_id']
    insert_post(None, None, data['reply'], 'reply', None, id,parent_id)

    if type == 'review':
        return redirect(url_for('template_review_page', id=parent_id))
    return redirect(url_for('template_topic_page', id=parent_id))

@app.route('/inlineReply/<int:review_id>/<int:parent_id>', methods=['POST'])
@requires_auth
def inline_reply(review_id, parent_id):
    data = request.form
    type = data['type']
    id = retrieve_user_id_by_sub(session.get('user').get('user_sub'))['user_id']
    insert_post(None, None, data['reply'], 'reply', None, id, parent_id)

    if type == 'review':
        return redirect(url_for('template_review_page', id=review_id))
    return redirect(url_for('template_topic_page', id=review_id))

@app.route('/results', methods=['POST'])
def results():
    query = request.form.get('query')
    posts = retrieve_all_posts(query)
    games = game_search(query, 10)
    return render_template("results.html", games=games, posts=posts, user=session.get('user'))

@app.route('/deletePost', methods=['POST'])
@requires_auth
def delete_post():
    data = request.form
    post_id = data['post_id']
    delete_id = data['delete_id']
    type = data['type']

    delete_content(delete_id)
    if post_id == delete_id:
        return redirect(url_for('home'))
    
    if type == 'review':
        return redirect(url_for('template_review_page', id=post_id))
    
    return redirect(url_for('template_topic_page', id=post_id))
