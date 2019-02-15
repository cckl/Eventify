import os

from flask import Flask, flash, render_template, redirect, request, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import User, Artist, Event, UserArtistLink, UserEventLink
from model import connect_to_db, db
import spotify


app = Flask(__name__)
app.secret_key = os.environ['FLASK_APP_KEY']
app.jinja_env.undefined = StrictUndefined

# function called a hook that can be run before anything else
# look into Flask hook
# use for session protected routes to check if user is logged in etc.


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
            return redirect('/get-top-40')
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

        # get user profile
        user_data = spotify.get_user_profile(access_token)

        # add user spotify info to database
        # also need condition to make sure this isn't re-added every time.
        # check if None?
        user_spotify_url = user_data['external_urls']['spotify']
        user_img = user_data['images'][0]['url']

        user = User.query.filter_by(username=session['user']).first()
        user.spotify_url = user_spotify_url
        user.img = user_img

        # add user top artists to database
        # need to get formatted res list of tuplesself.
        # iterate over it and add to artists database
        # then add the relationship to db?
        # get top artists
        response = spotify.get_top_artists(access_token)
        artists = spotify.format_artist_data(response)

        for artist in artists:
            artist_name = artist[1]
            artist_spotify_url = artist[2]
            artist_img = artist[3]

            # if artist already exists in db, skip and go to nextself
            # if artist doesn't exist, add to db
            if Artist.query.filter_by(name=artist_name).first():
                continue
            else:
                artist = Artist(name=artist_name, spotify_url=artist_spotify_url, img=artist_img)
                db.session.add(artist)

        db.session.commit()

        return render_template("top-40.html", artists=artists, all_data=response, user=user_data)


if __name__ == "__main__":
    app.debug = True

    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(port=5000, host='0.0.0.0')

    session.clear()
