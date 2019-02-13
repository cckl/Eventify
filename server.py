import os
from flask import Flask, flash, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

import spotify

app = Flask(__name__)
app.secret_key = 'demuja'
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def show_homepage():
    """Display homepage."""

    spotify_auth_url = spotify.get_auth_url()

    return render_template("homepage.html",  spotify_auth_url=spotify_auth_url)


@app.route('/spotify-auth')
def authorize_spotify():
    """Spotify authorization callback."""

    response = spotify.get_auth_token()
    print('THIS IS THE RESPONSE')
    print(response)
    print('\n\n\n')

    flash("Succesfully logged into Spotify!")
    session['spotify_token'] = response['access_token']
    print('THIS IS THE SESSION')
    print(session)
    print('\n\n\n')

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

    return render_template("top-40.html", artists=formatted_res, all_data=response, user=user)


if __name__ == "__main__":
    app.debug = True
    app.run(port=5000, host='0.0.0.0')
