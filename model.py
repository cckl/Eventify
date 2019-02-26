"""Models and database functions for project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


########################################
# Model definitions

class User(db.Model):
    """User of website."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    spotify_url = db.Column(db.String(200))
    img = db.Column(db.String(200))

    # https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
    artists = db.relationship('Artist', secondary='users_artists_link')
    events = db.relationship('Event', secondary='users_events_link')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<User: user_id={self.user_id}, username={self.username}, spotify_url={self.spotify_url}, img={self.img}>"


class Artist(db.Model):
    """Artist from Spotify."""

    __tablename__ = 'artists'

    artist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    spotify_url = db.Column(db.String(200), nullable=False)
    img = db.Column(db.String(200))

    users = db.relationship('User', secondary='users_artists_link')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Artist: artist_id={self.artist_id}, name={self.name}, spotify_url={self.spotify_url}, img_src={self.img}>"


class UserArtistLink(db.Model):
    """Users' top artists from Spotify."""

    # https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    __tablename__ = 'users_artists_link'

    users_artists_link_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'))
    created_at = db.Column(db.DateTime(timezone=True))

    users = db.relationship('User', backref='users_artists_link')
    artists = db.relationship('Artist', backref='users_artists_link')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserTopArtist: query_id={self.users_artists_link_id},  user_id={self.user_id}, artist_id={self.artist_id}>"


class Event(db.Model):
    """Event from Eventbrite."""

    __tablename__ = 'events'

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    venue = db.Column(db.String(150))
    address = db.Column(db.String(250))
    eventbrite_url = db.Column(db.String(250), nullable=False)
    img = db.Column(db.String(250))

    users = db.relationship('User', secondary="users_events_link")

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<Event: event_id={self.event_id},  name={self.name}, date={self.starts_at}, venue={self.venue}, url={self.eventbrite_url}>"


class UserEventLink(db.Model):
    """Users' liked events from Eventbrite."""

    __tablename__ = 'users_events_link'

    users_events_link_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    created_at = db.Column(db.DateTime(timezone=True))

    users = db.relationship('User', backref='users_events_link')
    events = db.relationship('Event', backref='users_events_link')

    def __repr__(self):
        """Provide representation of class attributes when printed."""

        return f"<UserLikedEvent: like_id={self.users_events_link_id},  user_id={self.user_id}, event_id={self.event_id}>"


#####################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///appdb'):
    """Connect the database to the Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


#####################################################################
# Example testdb data

def test_data():
    """Seeds testdb test database with example data."""

    user1 = User(username='user1', password='password', spotify_url='www.spotify.com', img='www.img.com')

    db.session.add(user1)

    db.session.commit()


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    db.create_all()
    print("👾 Connected to DB 👾")
