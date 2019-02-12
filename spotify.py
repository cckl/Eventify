"""Gets Spotify authorization credentials."""

import os
import base64

from flask import request

SPOTIFY_AUTHORIZATION_URL='https://accounts.spotify.com/authorize'
SPOTIFY_REDIRECT_URI='http://localhost:5000/spotify-auth'
SPOTIFY_CLIENT_ID=os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIFY_TOKEN_ENDPOINT='https://accounts.spotify.com/api/token'


def get_auth_url():
    """Generates Spotify authorization URL."""

    credentials = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': 'user-library-read user-top-read user-read-private'
    }

    auth_url = SPOTIFY_AUTHORIZATION_URL + '?client_id=' + credentials['client_id'] + '&response_type=' + credentials['response_type'] + '&redirect_uri=' + credentials['redirect_uri'] + '&scope=' + credentials['scope']

    return auth_url


def get_auth_token():
    """Exchange Spotify authorization code with access token."""

    auth_code = request.args.get('code')
    # auth_code = request.args['code']
    print(auth_code)

    request_params = {
        'grant_type': 'authorization_code',
        'code': str(auth_code),
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }

    client_encoded_str = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode('ascii'))
    print(client_encoded_str)

    header = {"Authorization": f"Basic {client_encoded_str.decode('ascii')}"}
    print(header)

    response = requests.post(SPOTIFY_TOKEN_ENDPOINT, data=request_params, headers=headers)

    return response.json()
