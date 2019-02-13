"""Models and database functions for project."""

from flask import SQLAlchemy

db = SQLAlchemy()

#####################################################################
# Model definitions

class User(db.Model):
    """User of website."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)
    spotify_url = db.Column(db.String(150))
    img = db.Column(db.String(150))

    # https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
    # create relationship with Artist class and association table of users' top artists
    artists = db.relationship('Artist', secondary='users_top_artists')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<User: user_id={self.user_id}, username={self.username}, spotify_url={self.spotify_url}, img_src={self.img}>"


class Artist(db.Model):
    """Artist from Spotify."""

    __tablename__ = 'artists'

    artist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    artist_name = db.Column(db.String(75), nullable=False)
    spotify_url = db.Column(db.String(150), nullable=False))
    img = db.Column(db.String(150))

    users = db.relationship('User', secondary='users_top_artists')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Artist: artist_id={self.artist_id}, name={self.artist_name}, spotify_url={self.spotify_url}, img_src={self.img}>"


class UserTopArtist(db.Model):
    """Users' top artists from Spotify."""

    # https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    # creating association table

    __tablename__ = 'users_top_artists'

    query_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'))

    user = db.relationship('User', backref='users_top_artists')
    artist = db.relationship('Artist', backref='users_top_artists')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserTopArtist: query_id={self.query_id},  user_id={self.user_id}, artist_id={self.artist_id}>"


class Event(db.Model):
    """Event from Eventbrite."""

    __tablename__ = 'events'

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event_name = db.Column(db.String(250), nullable=False)
    event_date = db.Column(db.DateTime)
    city = db.Column(db.String(50))
    eventbrite_url = db.Column(db.String(250))

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Event: event_id={self.event_id},  event_name={self.event_name}, date={self.event_date}, city={self.city}, url={elf.eventbrite_url}>"


class UserLikedEvent(db.Model):
    """Users' liked events from Eventbrite."""

    __tablename__ = 'users_liked_events'

    like_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))

    user = db.relationship('User', backref='users_liked_events')
    event = db.relationship('Event', backref='users_liked_events')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserLikedEvent: like_id={self.like_id},  user_id={self.user_id}, event_id={self.event_id}>"
