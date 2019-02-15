import os
from flask import Flask, flash, render_template, redirect, request, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import User, Artist, Event, UserArtistLink, UserEventLink, connect_to_db, db
import spotify


app = Flask(__name__)
app.secret_key = os.environ['FLASK_APP_KEY']
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def show_homepage():
    """Display homepage."""

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
    try:
        user = User.query.filter_by(username=username).one()
    except:
        flash('No user with that username was found. Please try again or register an account.')
        return render_template("login.html")

    user_password = User

    if password == user.password:
        session['user'] = username
        flash('Successfully logged in 😸')
        return redirect('/get-top-40')
    else:
        flash('Sorry, that password isn\'t correct 😧 Try again.')
        print(user)
        print(user.password)
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
    if User.query.filter_by(username = username).first():
        flash('Sorry, an account with that username already exists ☹️')
        return render_template("register.html")
    else:
        db.session.add(User(username=username, password=password))
        db.session.commit()
        # creates a user session
        session['user'] = username
        print(session)
        flash('Successfully created an account. 🐙')
        return redirect('/get-top-40')


@app.route('/logout')
def logout():
    """Logout."""

    session.clear()
    print(session)

    return redirect("/")


@app.route('/get-top-40')
def get_top_40():
    """Display page to login to Spotify."""

    print(session)

    if 'user' not in session:
        flash('Please login or register 👋🏻')
        return redirect('/')
    if 'spotify_token' in session:
        flash('You are already logged in to Spotify.')
        return redirect('/top-40')
    else:
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

    # print('THIS IS THE RESPONSE')
    # print(response)
    # print('\n\n\n')
    # print('THIS IS THE SESSION')
    # print(session)
    # print('\n\n\n')

    flash("Succesfully logged into Spotify! 👾")
    session['spotify_token'] = response['access_token']
    # 
    # print('OUR SESSION')
    # print(session)

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

    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(port=5000, host='0.0.0.0')
