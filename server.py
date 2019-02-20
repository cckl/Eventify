"""Runs the application."""

from app import app
from model import connect_to_db


if __name__ == "__main__":
    app.debug = True

    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(port=5000, host='0.0.0.0')
