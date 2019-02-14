import os
from flask import Flask, flash, render_template, redirect, request, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
# should import request from flask here, and then pass it in to the spotify.py functions
# pass the context, not import

import spotify


app = Flask(__name__)
app.secret_key = os.environ['FLASK_APP_KEY']
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def show_homepage():
    """Display homepage."""

    return render_template("homepage.html")


@app.route('/login')
def show_login():
    """Display user login page."""

    return render_template("login.html")


@app.route('/logout')
def logout():
    """Logout."""

    session.clear()
    print(session)

    return redirect("/")


@app.route('/register')
def show_registration():
    """Display user registration page."""

    return render_template("register.html")


@app.route('/get-top-40')
def get_top_40():
    """Display page to login to Spotify."""

    spotify_auth_url = spotify.get_auth_url()

    return render_template("get-top-40.html",  spotify_auth_url=spotify_auth_url)


@app.route('/spotify-auth')
def authorize_spotify():
    """Spotify authorization callback."""

    response = spotify.get_access_token(request)

    # if 'spotify_token' in session:
    #     flash('Already logged in to Spotify!')
    #     return redirect("/top-40")
    # else:
    #     flash("Succesfully logged into Spotify!")
    #     session['spotify_token'] = response['access_token']
    #     return redirect("/top-40")

    print('THIS IS THE RESPONSE')
    print(response)
    print('\n\n\n')
    print('THIS IS THE SESSION')
    print(session)
    print('\n\n\n')

    flash("Succesfully logged into Spotify!")
    session['spotify_token'] = response['access_token']

    print('OUR SESSION')
    print(session)

    return redirect("/top-40")


@app.route('/top-40')
def show_top_40():
    """Display user's top 40 Spotify artists."""

    access_token = session['spotify_token']

    # get top artists
    response = spotify.get_top_artists(access_token)
    formatted_res = spotify.format_artist_data(response)

    # get user get_user_profile
    user = spotify.get_user_profile(access_token)

    print('OUR SESSION')
    print(session)

    return render_template("top-40.html", artists=formatted_res, all_data=response, user=user)


if __name__ == "__main__":
    app.debug = True
    app.run(port=5000, host='0.0.0.0')
