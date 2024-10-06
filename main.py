from flask import Flask,render_template
from igdbAPI import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html', user_logged_in='user1') #user_logged_in is just for testing the navbar

@app.route('/user/profile')
def user_profile():
    return render_template('user_profile.html', active_page='profile')

@app.route('/user/reviews')
def user_reviews():
    return render_template('user_reviews.html', active_page='reviews')
@app.route('/user/settings')
def user_settings():
    return render_template('user_settings.html', active_page='settings')



@app.route('/review/<string:name>')
def template_review_page(name):
    data = get_game_data(name)

    TODO: replace the return with the html template with info from data
    data.get("coverImageUrl")
    data.get("gameModes")
    data.get("genres")
    data.get("companies")
    data.get("playerPerspectives")
    data.get("similarGames")
    data.get("storyline")
    data.get("summary")
    data.get("themes")
    return None


@app.route('/discussion/<string:name>')
def template_review_page1(name):
    # TODO: replace the return with the html template
    return None



