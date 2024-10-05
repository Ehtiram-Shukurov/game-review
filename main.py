from flask import Flask, render_template
from igdbAPI import *

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route('/review/<string:name>')
def template_review_page(name):
    data = get_game_data(name)

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
    return None


@app.route('/game/<string:name>')
def template_game_page(name):
    game_data = get_game_data("The Elder Scrolls V: Skyrim")
    # reviews = get_reviews(); TODO: implement get reviews from database
    return render_template("game.html", game_data=game_data, reviews=reviews)
