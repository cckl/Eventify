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

# TODO: Check for user login through authentication, not just sessions
# TODO: Input validation for all forms
# http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Hi. Please login or register 👋')
            print(session)
            return redirect(url_for('show_homepage'))
    return wrap


def logged_in(f):
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
            flash('Hi. Please login to Spotify 🎧')
            print(session)
            return redirect(url_for('get_top_40'))
    return wrap


@app.route('/')
@logged_in
def show_homepage():
    """Display homepage."""

    return render_template("homepage.html")


@app.route('/login')
@logged_in
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
            flash('Successfully logged in 😸')
            return redirect('/top-40')
        else:
            flash('Sorry, that username or password isn\'t correct 😧 Try again.')
            return render_template("login.html")
    else:
        flash('Sorry, that username or password isn\'t correct 😧 Try again.')
        return render_template("login.html")


@app.route('/register')
@logged_in
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
        flash('Sorry, an account with that username already exists ☹️')
        return render_template("register.html")
    else:
        helper.add_user_db(username, password)

        # creates a user session
        session['user'] = username
        session['logged_in'] = True
        flash('Successfully created an account. 🐙')
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

    flash("Succesfully logged into Spotify! 👾")
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
    if helper.check_spotify_not_in_db(username):
        helper.add_user_spotify_db(access_token)
        helper.add_artist_db(access_token)
        helper.add_user_artist_link(access_token)

    return render_template("top-40.html", artists=artists, user=user_data)


@app.route('/event-search')
@login_required
@spotify_login_required
def search_events():
    """Search for events using the Eventbrite API."""

    return render_template("event-search.html")


@app.route('/event-search', methods=['POST'])
def process_event_search():
    """Returns event search results from the Eventbrite API."""

    city = request.form.get('city')
    distance = request.form.get('distance')

    access_token = session['access_token']
    artists = spotify.get_top_artists(access_token)
    results = eventbrite.search_batch_events(artists, city, distance)

    # TODO: check for valid location input
    if results == 'location invalid':
        flash('You entered an invalid location. Please try your search again.')
        return redirect('/event-search')
    elif results:
        helper.add_events_db(results)
        helper.add_user_event_link(results)
        return jsonify(results)
    else:
        return jsonify(results)


@app.route('/recommended', methods=['POST'])
def search_recommended_events():
    """Returns recommended event search results from the Eventbrite API using Spotify related artists."""

    city = request.form.get('city')
    distance = request.form.get('distance')

    access_token = session['access_token']
    related_artists = spotify.get_related_artists(access_token)
    results = eventbrite.search_batch_events(related_artists, city, distance)

    return jsonify(results)
