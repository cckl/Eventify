import os
import unittest
from unittest import TestCase

from config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI
from model import connect_to_db, db, test_data
from views import app
import spotify

# http://flask.pocoo.org/docs/1.0/testing/
# https://requests-mock.readthedocs.io/en/latest/

class UserTest(unittest.TestCase):
    """Tests for user actions."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        test_data()

    def test_register(self):
        response = self.client.post('/register', data={'username': 'username', 'password': 'password'}, follow_redirects=True)
        self.assertIn(b"Successfully created an account", response.data)
        self.assertIn(b"See your top 40 artists on Spotify!", response.data)

    def test_register_fail(self):
        response = self.client.post('/register', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)
        self.assertIn(b"Sorry, an account with that username already exists", response.data)

    def test_login(self):
        response = self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)
        self.assertIn(b"See your top 40 artists on Spotify!", response.data)

    def test_login_fail(self):
        response = self.client.post('/login', data={'username': 'username', 'password': 'acdbe'}, follow_redirects=True)
        self.assertIn(b"Sorry, that username or password", response.data)

    def tearDown(self):
        db.session.close()
        db.drop_all()


class SpotifyTests(unittest.TestCase):
    """Tests Spotify login and authentication with user logged in."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = 'user1'

    def test_valid_auth_url(self):
        auth_url = spotify.get_auth_url()
        self.assertIn('user-top-read', auth_url)
        self.assertIn(SPOTIFY_CLIENT_ID, auth_url)

    def test_top40_spotify_logged_out(self):
        response = self.client.get('/top-40', follow_redirects=True)
        self.assertIn(b"Please login to Spotify", response.data)

    def test_top40_spotify_logged_in(self):
        response = self.client.get('/top-40', follow_redirects=True)
        self.assertIn(b"Welcome", response.data)


class ViewTestsLoggedIn(unittest.TestCase):
    """View tests with user logged into session."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = 'user1'

    def test_login_spotify_page(self):
        result = self.client.get('/get-top-40', follow_redirects=True)
        self.assertIn(b"See your top 40 artists on Spotify!", result.data)


class ViewTestsLoggedOut(unittest.TestCase):
    """View tests without user logged into session."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn(b"<h1>Login or register</h1>", result.data)

    def test_register_page(self):
        result = self.client.get('/register')
        self.assertIn(b"Enter a username between 1-25 characters.", result.data)

    def test_login_page(self):
        result = self.client.get('/login')
        self.assertIn(b"<h2>Login to your account</h2>", result.data)

    def test_login_spotify_page_fail(self):
        result = self.client.get('/get-top-40', follow_redirects=True)
        # FIXME: Testing for flash message text doesn't work?
        self.assertIn(b"Login or register", result.data)

    def test_top40_fail(self):
        result = self.client.get('/top-40', follow_redirects=True)
        # FIXME: Testing for flash message text doesn't work?
        self.assertIn(b"Login or register", result.data)


if __name__ == "__main__":
    unittest.main()
