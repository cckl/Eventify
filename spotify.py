"""Handles Spotify authorization, access tokens, and API requests."""

import os
import base64
import requests

from flask import request

SPOTIFY_AUTHORIZATION_URL='https://accounts.spotify.com/authorize'
SPOTIFY_REDIRECT_URI='http://localhost:5000/spotify-auth'
SPOTIFY_CLIENT_ID=os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET=os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_TOKEN_ENDPOINT='https://accounts.spotify.com/api/token'


def get_auth_url():
    """Generate Spotify authorization URL."""

    # need auth url to login and generate authorization code
    # specify credentials so spotify api authorizes the get request
    credentials = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': 'user-library-read user-top-read user-read-private'
    }

    auth_url = SPOTIFY_AUTHORIZATION_URL + '?client_id=' + credentials['client_id'] + '&response_type=' + credentials['response_type'] + '&redirect_uri=' + credentials['redirect_uri'] + '&scope=' + credentials['scope']

    return auth_url


def get_auth_token():
    """Exchange Spotify authorization code for access token via POST request."""

    # gets the value of 'code' from the query string in the auth url
    auth_code = request.args.get('code')

    request_params = {
        'grant_type': 'authorization_code',
        'code': str(auth_code),
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }

    # https://github.com/yspark90/UniMuse/blob/master/UniMuse/spotify.py
    # https://docs.python.org/2/library/base64.html
    # need to import base64 to use encode and decode methods
    # the header, as specified in the docs, needs to be a base64 encoded string that has
    # the client ID and secret key. can use base64 to encode and decode
    client_encoded_str = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode('ascii'))
    print('THIS IS ENCODED STRING')
    print(client_encoded_str)
    print('\n\n\n')

    headers = {"Authorization": f"Basic {client_encoded_str.decode('ascii')}"}
    print('THIS IS THE HEADER')
    print(headers)
    print('\n\n\n')

    # http://flask.pocoo.org/docs/1.0/reqcontext/
    # http://docs.python-requests.org/en/master/user/quickstart/
    # https://www.pluralsight.com/guides/web-scraping-with-request-python
    # need to submit auth code to spotify's token endpoint to get access token in return
    # requests.post takes the endpoint, the request parameters as a dictionary, and header
    response = requests.post(SPOTIFY_TOKEN_ENDPOINT, data=request_params, headers=headers)

    # need to convert to json so i can access info more easily
    return response.json()


def get_top_artists(access_token):
    """Get a user's top 40 artists."""

    # https://www.dataquest.io/blog/python-api-tutorial/
    SPOTIFY_TOP_ARTISTS_ENDPOINT = 'https://api.spotify.com/v1/me/top/artists'

    # necessary query params for playlist endpoint
    query_params = {
        'time_range': 'long_term',
        'limit': '40'
    }

    url = SPOTIFY_TOP_ARTISTS_ENDPOINT + "?time_range=" + query_params['time_range'] + "&limit=" + query_params['limit']
    print('THIS IS THE URL')
    print(url)
    print('\n\n\n')

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    return response.json()


def format_artist_data(response):
    """Format top artist JSON data as a list of tuples: index, artist, url, and image."""

    numbered_list = []

    for index, item in enumerate(response['items'], 1):
        numbered_list.append((index,
                            item['name'],
                            item['external_urls']['spotify'],
                            item['images'][2]['url']))

    return numbered_list


def get_user_profile(access_token):
    """Get Spotify profile information about the current user."""

    SPOTIFY_USER_ENDPOINT = 'https://api.spotify.com/v1/me'

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(SPOTIFY_USER_ENDPOINT, headers=headers)

    return response.json()
