"""Models and database functions for project."""

from flask_sqlalchemy import SQLAlchemy

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
    artists = db.relationship('Artist', secondary='users_artists_link', back_populates='user')
    events = db.relationship('Event', secondary='users_events_link', back_populates='user')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<User: user_id={self.user_id}, username={self.username}, spotify_url={self.spotify_url}, img_src={self.img}>"


class Artist(db.Model):
    """Artist from Spotify."""

    __tablename__ = 'artists'

    artist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    spotify_url = db.Column(db.String(150), nullable=False)
    img = db.Column(db.String(150), nullable=False)

    users = db.relationship('User', secondary='users_artists_link', back_populates='artist')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Artist: artist_id={self.artist_id}, name={self.artist_name}, spotify_url={self.spotify_url}, img_src={self.img}>"


class UserArtistLink(db.Model):
    """Users' top artists from Spotify."""

    # https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    # creating association table

    __tablename__ = 'users_artists_link'

    users_artists_link_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'))
    created_at = db.Column(db.DateTime(timezone=True))

    # user = db.relationship('User', backref='users_top_artists')
    # artist = db.relationship('Artist', backref='users_top_artists')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserTopArtist: query_id={self.query_id},  user_id={self.user_id}, artist_id={self.artist_id}>"


class Event(db.Model):
    """Event from Eventbrite."""

    __tablename__ = 'events'

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime(timezone=True))
    starts_at = db.Column(db.String(50))
    eventbrite_url = db.Column(db.String(250))

    users = db.relationship('User', secondary="users_events_link", back_populates='event')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Event: event_id={self.event_id},  event_name={self.event_name}, date={self.event_date}, city={self.city}, url={self.eventbrite_url}>"


class UserEventLink(db.Model):
    """Users' liked events from Eventbrite."""

    __tablename__ = 'users_events_link'

    users_events_link_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))

    # can eliminate the need for these with a backref in Event
    # user = db.relationship('User', backref='users_liked_events')
    # event = db.relationship('Event', backref='users_liked_events')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserLikedEvent: like_id={self.like_id},  user_id={self.user_id}, event_id={self.event_id}>"


#####################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to the Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    db.create_all()
    print("Connected to DB ◕ ◡ ◕")
