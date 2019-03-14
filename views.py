"""Views for application."""

import os
from functools import wraps
from flask import g, Flask, flash, jsonify, render_template, redirect, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from app import app
import eventbrite
import helper
from model import User, Artist, Event, UserArtistLink, UserEventLink
from model import connect_to_db, db
import spotify


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('show_homepage'))
    return wrap


def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('show_top_40'))
        else:
            return f(*args, **kwargs)
    return wrap


def spotify_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'spotify_logged_in' in session:
            print(session)
            return f(*args, **kwargs)
        else:
            return redirect(url_for('get_top_40'))
    return wrap


@app.route('/')
@logout_required
def show_homepage():
    """Display homepage."""

    session.clear()
    return render_template("homepage.html")


@app.route('/login')
@logout_required
def show_login():
    """Display user login page."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def process_login():
    """Process user login."""

    username = request.form.get('username')
    password = request.form.get('password')

    # checks for existing user with matching credentials
    user = User.query.filter_by(username=username).first()
    if user:
        if password == user.password:
            session['user'] = username
            session['logged_in'] = True
            return redirect('/top-40')
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/register')
@logout_required
def show_registration():
    """Display user registration page."""

    return render_template("register.html")


@app.route('/register', methods=['POST'])
def process_registration():
    """Process user registration."""

    username = request.form.get('username')
    password = request.form.get('password')

    # checks to ensure a unique username account is being added
    if User.query.filter_by(username=username).first():
        return render_template("register.html")
    else:
        helper.add_user_db(username, password)

        # creates a user session
        session['user'] = username
        session['logged_in'] = True
        return redirect('/get-top-40')


@app.route('/logout')
@login_required
def logout():
    """Logout user."""

    session.clear()
    return redirect("/")


@app.route('/get-top-40')
@login_required
def get_top_40():
    """Display Spotify login."""

    print(session)
    spotify_auth_url = spotify.get_auth_url()
    return render_template("get-top-40.html", spotify_auth_url=spotify_auth_url)


@app.route('/spotify-auth')
@login_required
def authorize_spotify():
    """Spotify authorization callback."""

    response = spotify.get_access_token(request)
    session['access_token'] = response['access_token']
    session['refresh_token'] = response['refresh_token']
    session['spotify_logged_in'] = True

    return redirect("/top-40")


@app.route('/top-40')
@login_required
@spotify_login_required
def show_top_40():
    """Display user's top 40 Spotify artists."""

    access_token = session['access_token']
    user_data = spotify.get_user_profile(access_token)
    artists = spotify.get_top_artists(access_token)
    username = session['user']

    # after classes encapsulate instantiation, can create function "add user"
    # should extract the user/artist creation process to another filter_events
    # 'if': can this be extracted

    # pull out user from db and keep the object saved to variable
    # otherwise constantly querying db for user object

    # session is best kept at the view level -- might backfire in testing
    if helper.check_spotify_not_in_db(username):
        helper.add_user_spotify_db(access_token)
        helper.add_artist_db(access_token)
        helper.add_user_artist_link(access_token)

    return render_template("top-40.html", artists=artists, user=user_data)


@app.route('/event-search', methods=['POST'])
def process_event_search():
    """Return event search results from the Eventbrite API."""

    city = request.form.get('city')
    distance = request.form.get('distance')

    access_token = session['access_token']
    artists = spotify.get_top_artists(access_token)
    results = eventbrite.search_batch_events(artists, city, distance)

    # TODO: check for valid location input
    print(results)
    if results:
        helper.add_events_db(results)
        helper.add_user_event_link(results)
        return jsonify(results)
    else:
        return jsonify(results)


@app.route('/recommended', methods=['POST'])
def search_recommended_events():
    """Return recommended event search results from the Eventbrite API using Spotify related artists."""

    city = request.form.get('city')
    distance = request.form.get('distance')

    access_token = session['access_token']
    related_artists = spotify.get_related_artists(access_token)
    results = eventbrite.search_batch_events(related_artists, city, distance)

    return jsonify(results)


@app.route('/explore')
@login_required
@spotify_login_required
def explore():
    """Display explore page with other user info."""

    all_users = User.query.all()
    users = []
    users_artists = {}

    for user in all_users:
        if user.username != session['user']:
            users.append((user.username, user.spotify_url, user.img))
            user_artists = []
            for artist in user.artists:
                user_artists.append((artist.name, artist.spotify_url, artist.img))
            users_artists[user.username] = user_artists

    return render_template("explore.html", users=users, artists=users_artists)
