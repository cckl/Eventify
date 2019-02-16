"""Helper functions for adding user, artist, and event info to database."""

import os
from flask import Flask, flash, render_template, redirect, request, session

import views
import spotify
from model import User, Artist, Event, UserArtistLink, UserEventLink
from model import connect_to_db, db


def add_user_db(access_token):
    """Add user info to database after Spotify login."""

    user_data = spotify.get_user_profile(access_token)

    user_spotify_url = user_data['external_urls']['spotify']
    user_img = user_data['images'][0]['url']

    user = User.query.filter_by(username=session['user']).first()
    user.spotify_url = user_spotify_url
    user.img = user_img

    db.session.commit()


def add_artist_db(access_token):
    """Add artist info to database after Spotify login."""

    # get artist info
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


def add_user_artist_link(access_token):
    """Add user and artist info to association table."""
    pass
