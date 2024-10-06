import json
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


app.secret_key = os.environ['AUTH0_SECRET_KEY']


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ['AUTH0_CLIENT_ID'],
    client_secret=os.environ['AUTH0_SECRET'],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ['AUTH0_DOMAIN']}/.well-known/openid-configuration',
)


# Controllers API
# TODO change home page to the following 
# below is the code from the example downloaded from auth0
#@app.route("/a")
#def home():
#    return render_template(
#        "home.html",
#        session=session.get("user"),
#        pretty=json.dumps(session.get("user"), indent=4),
#    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(token)
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
        + os.environ['AUTH0_DOMAIN']
        + "/v2/logout?"
        + urlencode(
            {
                # replace hello_world with actual function for homepage endpoint
                "returnTo": url_for("hello_world", _external=True),
                "client_id": os.environ['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        )
    )

app.run(host='0.0.0.0', port =3000)