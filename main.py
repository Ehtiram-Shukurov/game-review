from flask import Flask
from igdbAPI import *
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/review/<str:name>')
def templateReveiwPage(name):
    data = getGameData(name)



    #TODO: replace the return with the html template with info from data
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

@app.route('/discussion/<str:name>')
def templateReveiwPage():
    #TODO: replace the return with the html template
    return None