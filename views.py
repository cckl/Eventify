"""Views for application."""

import os
from flask import Flask, flash, render_template, redirect, request, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from app import app
import eventbrite
import helper
from model import User, Artist, Event, UserArtistLink, UserEventLink
from model import connect_to_db, db
import spotify

# from config import FLASK_APP_KEY

# app = Flask(__name__)
# app.secret_key = 'FLASK_APP_KEY'
# app.jinja_env.undefined = StrictUndefined


# TODO: Check for user login through authentication, not just sessions
# Use Flask.g and decorators

@app.route('/')
def show_homepage():
    """Display homepage."""

    session.clear()
    print(session)

    if 'user' in session:
        if 'spotify_token' in session:
            flash('You are already logged in to Spotify.')
            return redirect('/top-40')
        else:
            flash('You are already logged in.')
            return redirect('/get-top-40')
    else:
        return render_template("homepage.html")


@app.route('/login')
def show_login():
    """Display user login page."""

    if 'user' in session:
        if 'spotify_token' in session:
            flash('You are already logged in to Spotify.')
            return redirect('/top-40')
        else:
            flash('You are already logged in.')
            return redirect('/get-top-40')
    else:
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
            flash('Successfully logged in 😸')
            # FIXME: still redirecting to /get-top-40. maybe cuz spotify
            # doesn't automatically login?
            return redirect('/top-40')
        else:
            flash('Sorry, that password isn\'t correct 😧 Try again.')
            return render_template("login.html")
    else:
        flash('No user with that username was found. Please try again.')
        return render_template("login.html")


@app.route('/register')
def show_registration():
    """Display user registration page."""

    if 'user' in session:
        if 'spotify_token' in session:
            flash('You are already logged in to Spotify.')
            return redirect('/top-40')
        else:
            flash('You are already logged in.')
            return redirect('/get-top-40')
    else:
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
        db.session.add(User(username=username, password=password))
        db.session.commit()

        # creates a user session
        session['user'] = username
        flash('Successfully created an account. 🐙')
        return redirect('/get-top-40')


@app.route('/logout')
def logout():
    """Logout user."""

    session.clear()

    return redirect("/")


@app.route('/get-top-40')
def get_top_40():
    """Display Spotify login."""

    if 'user' not in session:
        flash('Please login or register 👋🏻')
        return redirect('/')
    if 'spotify_token' in session:
        flash('You are already logged in to Spotify.')
        return redirect('/top-40')
    else:
        spotify_auth_url = spotify.get_auth_url()
        return render_template("get-top-40.html", spotify_auth_url=spotify_auth_url)


@app.route('/spotify-auth')
def authorize_spotify():
    """Spotify authorization callback."""

    response = spotify.get_access_token(request)
    flash("Succesfully logged into Spotify! 👾")
    session['spotify_token'] = response['access_token']

    return redirect("/top-40")


@app.route('/top-40')
def show_top_40():
    """Display user's top 40 Spotify artists."""

    print(session)

    if 'spotify_token' not in session:
        if 'user' not in session:
            flash('Please login or register. 👋🏻')
            return redirect('/')
        else:
            flash('Please login to Spotify 🎧')
            return redirect('/get-top-40')
    else:
        access_token = session['spotify_token']

        # get user profile and artist info
        user_data = spotify.get_user_profile(access_token)
        response = spotify.get_top_artists(access_token)
        artists = spotify.format_artist_data(response)

        # add new user's info to db
        username = session['user']
        if helper.check_spotify_not_in_db(username):
            helper.add_user_db(access_token)
            helper.add_artist_db(access_token)
            helper.add_user_artist_link(access_token)

        return render_template("top-40.html", artists=artists, all_data=response, user=user_data)


@app.route('/event-search')
def search_events():
    """Search for events using the Eventbrite API."""

    # access_token = session['spotify_token']
    #
    #
    # s_response = spotify.get_top_artists(access_token)
    # artists = spotify.format_artist_data(s_response)
    #
    # events_list = eventbrite.get_events(artists)

    return render_template("event-search.html")


@app.route('/event-results', methods=['POST'])
def process_event_search():
    """Returns event search results from the Eventbrite API."""

    # Set up basic input to test API requests first
    # artist = request.form.get('artist')
    city = request.form.get('city')
    distance = request.form.get('distance')

    access_token = session['spotify_token']
    s_response = spotify.get_top_artists(access_token)
    artists = spotify.format_artist_data(s_response)

    response = eventbrite.get_events(artists, city, distance)

    # response = eventbrite.get_events_data(artist, city, distance)

    # TODO: where to add error code checking in general?
    # check for valid location input
    if response == 'location invalid':
        flash('You entered an invalid location. Please try your search again.')
        return redirect('/event-search')
    else:
        return render_template("event-results.html", events=response)

# https://realpython.com/the-model-view-controller-mvc-paradigm-summarized-with-legos/
