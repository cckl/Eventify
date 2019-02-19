"""Views for application."""

import os
from flask import Flask, flash, render_template, redirect, request, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import User, Artist, Event, UserArtistLink, UserEventLink
from model import connect_to_db, db
import spotify
import eventbrite
import helper

# This doesn't really belong in views. I'd suggest something like a main,py or app.py to make it clear to the reader where the app begins.
app = Flask(__name__)
app.secret_key = os.environ['FLASK_APP_KEY']
app.jinja_env.undefined = StrictUndefined

# session protected routes: use hook or Flask.g?
# user not logged in to app or Spotify --> "/"
# user logged in to app
    # first time user: "/get-top-40"
    # returning user "/top-40"

@app.route('/')
def show_homepage():
    """Display homepage."""

    session.clear()  # Does this line make the following session checks always false?

    # This repeated structure can be extracted. We spoke about using a flask lifecycle hook or decorator as ways to do this.
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

    # I'd expect some kind of form validation to be required here.
    username = request.form.get('username')
    password = request.form.get('password')

    # checks for existing user with matching credentials
    user = User.query.filter_by(username=username).first()
    if user:
        if password == user.password:
            session['user'] = username
            flash('Successfully logged in 😸')
            return redirect('/top-40')
        else:
            flash('Sorry, that password isn\'t correct 😧 Try again.')
            return render_template("login.html")
    else:
        # It's common to see the message for this branch be the same as incorrect password
        # to prevent attackers from probing for users.
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
        # This use of db inline stands out to me.
        # Typically there's some abstraction of what registering "does".
        # Extracting this will make testing easier; right now, you'd be dealing with a hard coupling of this code in your test.
        db.session.add(User(username=username, password=password))
        db.session.commit()

        # creates a user session
        session['user'] = username
        # You might try using python's logging package for this print call.
        print(session)
        flash('Successfully created an account. 🐙')
        return redirect('/get-top-40')


@app.route('/logout')
def logout():
    """Logout user."""

    session.clear()

    return redirect("/")


@app.route('/get-top-40')
def get_top_40():
    """Display login page to Spotify."""

    print(session)

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
        # You might think about all the ways calling a partner's api can fail.
        # We use a library called tenacity when calling services to add resilence.
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

    return render_template("event-search.html")


@app.route('/event-results', methods=['POST'])
def process_event_search():
    """Returns event search results from the Eventbrite API."""

    # Set up basic input to test API requests first
    # This input could be validated
    artist = request.form.get('artist')
    city = request.form.get('city')

    events = eventbrite.get_events_data(artist, city)

    return render_template("event-results.html", events=events)


# https://realpython.com/the-model-view-controller-mvc-paradigm-summarized-with-legos/
