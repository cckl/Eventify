"""Handles Spotify authorization, access tokens, and API requests."""

import os
import base64
from flask import session
import urllib
import requests

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

SPOTIFY_AUTHORIZATION_URL='https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_ENDPOINT='https://accounts.spotify.com/api/token'
SPOTIFY_USER_ENDPOINT = 'https://api.spotify.com/v1/me'
SPOTIFY_TOP_ARTISTS_ENDPOINT = 'https://api.spotify.com/v1/me/top/artists'
SPOTIFY_RELATED_ARTISTS_ENDPOINT ='https://api.spotify.com/v1/artists'


def get_auth_url():
    """Return Spotify authorization URL."""


    payload = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': 'user-library-read user-top-read user-read-private'
    }

    url_args = urllib.parse.urlencode(payload)
    auth_url = f"{SPOTIFY_AUTHORIZATION_URL}/?{url_args}"
    return auth_url


def get_access_token(request):
    """Return Spotify access token."""


    auth_code = request.args.get('code')

    payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_code),
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }

    client_encoded_str = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode('ascii'))
    auth_header = {"Authorization": f"Basic {client_encoded_str.decode('ascii')}"}

    response = requests.post(SPOTIFY_TOKEN_ENDPOINT, data=payload, headers=auth_header)
    return response.json()


def refresh_token():
    """Return new Spotify access token in exchange for ref  resh token."""


    refresh_payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token']
    }

    client_encoded_str = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode('ascii'))
    refresh_auth_header = {"Authorization": f"Basic {client_encoded_str.decode('ascii')}"}

    response = requests.post(SPOTIFY_TOKEN_ENDPOINT, data=refresh_payload, headers=refresh_auth_header)
    response = response.json()
    access_token = response['access_token']

    return access_token


def get_top_artists(access_token):
    """Return a user's top 40 Spotify artists."""


    payload = {
        'time_range': 'medium_term',
        'limit': '40'
    }

    url_args = urllib.parse.urlencode(payload)
    url = f"{SPOTIFY_TOP_ARTISTS_ENDPOINT}/?{url_args}"

    auth_header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=auth_header)

    if response.status_code == 200:
        response = response.json()
        artists = format_artist_data(response)
        return artists

    elif response.status_code == 401:
        access_token = refresh_token()
        return get_top_artists(access_token)


def format_artist_data(response):
    """Return a list of formatted artist data in tuples: index, name, url, image, and id."""


    artists = []

    for index, item in enumerate(response['items'], 1):
        artists.append((index, item['name'], item['external_urls']['spotify'], item['images'][2]['url'], item['id']))

    return artists


def get_related_artists(access_token):
    """Return a list of related artists to top 40 Spotify artists in tuples: name, id."""


    top_artists = get_top_artists(access_token)

    related_artists = []

    for artist in top_artists:
        name = artist[0]
        id = artist[4]
        url = f"{SPOTIFY_RELATED_ARTISTS_ENDPOINT}/{id}/related-artists"
        auth_header = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=auth_header)

        if response.status_code == 200:
            response = response.json()
            filtered_artists = filter_related_artists(response)
            related_artists.extend(filtered_artists)

        elif response.status_code == 401:
            access_token = refresh_token()
            return get_related_artists(access_token)

    return related_artists


def filter_related_artists(response):
    """Return a list of 5 related artists with tuple-formatted name, id."""


    filtered_artists = []

    for i in range(0, 5):
        if response['artists']:
            artist = response['artists'][i]
            filtered_artists.append((artist['id'], artist['name']))

    return filtered_artists


def get_user_profile(access_token):
    """Return Spotify profile information about the current user."""


    auth_header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTIFY_USER_ENDPOINT, headers=auth_header)

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 401:
        access_token = refresh_token()
        return get_user_profile(access_token)
