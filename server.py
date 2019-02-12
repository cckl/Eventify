import os
from flask import Flask, render_template, redirect, session
# from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

# import testing
import spotify

app = Flask(__name__)
app.secret_key = 'demuja'
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def show_homepage():
    """Displays homepage."""

    spotify_auth_url = spotify.get_auth_url()

    return render_template("homepage.html",  spotify_auth_url=spotify_auth_url)

@app.route('/spotify-auth')
def authorize_spotify():

     return render_template("test.html")

if __name__ == "__main__":
    app.debug = True
    app.run(port=5000, host='0.0.0.0')
