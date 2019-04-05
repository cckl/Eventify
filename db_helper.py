"""Helper functions for adding user, artist, and event info to database."""

import os
from flask import Flask, flash, render_template, redirect, request, session
from datetime import datetime

from model import User, Artist, Event, UserArtistLink, UserEventLink, connect_to_db, db
import spotify
import views


def add_user_db(username, password):
    """Add username and password info to users table."""

    db.session.add(User(username=username, password=password))
    db.session.commit()


def check_spotify_not_in_db(username):
    """Check for existing Spotify data in users table."""

    current_user = User.query.filter_by(username=username).first()
    user_id = current_user.user_id

    return current_user.spotify_url == None


def add_user_spotify_db(access_token):
    """Add user info to users table after Spotify login."""

    # get user data from spotify response.json()
    user_data = spotify.get_user_profile(access_token)
    user_spotify_url = user_data['external_urls']['spotify']
    if user_data['images']:
        user_img = user_data['images'][0]['url']

    user = User.query.filter_by(username=session['user']).first()
    user.spotify_url = user_spotify_url
    if user_data['images']:
        user.img = user_img

    db.session.commit()


def add_artist_db(access_token):
    """Add artist info to artists table after Spotify login."""

    # get artist info from spotify response.json()
    artists = spotify.get_top_artists(access_token)

    for artist in artists:
        artist_name = artist[1]
        artist_spotify_url = artist[2]
        artist_img = artist[3]

        # if artist already exists in db, skip and go to next one
        # if artist doesn't exist, add to db
        if Artist.query.filter_by(name=artist_name).first():
            continue
        else:
            artist = Artist(name=artist_name, spotify_url=artist_spotify_url, img=artist_img)
            db.session.add(artist)

    db.session.commit()


def add_user_artist_link(access_token):
    """Add user and artist link info to association table."""

    # get current user from session
    username = session['user']
    current_user_id = User.query.filter_by(username=username).first().user_id

    # get list of artist info from spotify response.json()
    artists = spotify.get_top_artists(access_token)

    for artist in artists:
        name = artist[1]
        artist_id = Artist.query.filter_by(name=name).first().artist_id

        # instantiate user artist link object
        link = UserArtistLink(user_id=current_user_id, artist_id=artist_id, created_at=datetime.now())

        db.session.add(link)

    db.session.commit()


def add_events_db(results):
    """Add event listing info to events table."""

    for event in results:
        name = event['name']
        starts_at = event['starts_at']
        ends_at = event['ends_at']
        venue = event['venue']
        address = event['address']
        url = event['url']
        img = event['img']

        # checks for existing event in table. if found, skip
        if Event.query.filter_by(eventbrite_url=url).first():
            continue
        else:
            new_event = Event(name=name, starts_at=starts_at, ends_at=ends_at, venue=venue, address=address, eventbrite_url=url, img=img)
            db.session.add(new_event)

    db.session.commit()


def add_user_event_link(response):
    """Add user and event link info to association table."""

    username = session['user']
    current_user_id = User.query.filter_by(username=username).first().user_id

    for event in response:
        name = event['name']
        event_id = Event.query.filter_by(name=name).first().event_id

        # instantiate user event link object
        link = UserEventLink(user_id=current_user_id, event_id=event_id, created_at=datetime.now())

        db.session.add(link)

    db.session.commit()

# can be encapsulated in model.py classes
