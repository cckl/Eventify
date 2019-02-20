"""Handles Eventbrite authorization and API requests."""

import os
import urllib
import requests
import time
from config import EVENTBRITE_APP_KEY, EVENTBRITE_CLIENT_SECRET, EVENTBRITE_OAUTH_TOKEN

EVENTBRITE_SEARCH_ENDPOINT='https://www.eventbriteapi.com/v3/events/search'
EVENTBRITE_BATCH_ENDPOINT='https://www.eventbriteapi.com/v3/batch'

def get_events(artists, city, distance):
    """Search for events given a list of top 40 Spotify artists."""

    events_res = []

    # search eventbrite for each artist
    print(artists)

    for artist in artists:
        name = artist[1]

        city = '%20'.join(city.split())

        # FIXME: make sure artist is in the event name so random events don't show up
        query_params = {
            'q': name,
            'location.address': city,
            'location.within': distance,
            'categories': '103',
            'expand': 'venue'
        }

        url_args = '&'.join([f"{key}={urllib.parse.quote(val)}" for key, val in query_params.items()])
        url = f"{EVENTBRITE_SEARCH_ENDPOINT}/?{url_args}"

        headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}
        response = requests.get(url, headers=headers)
        response = response.json()
        # print('\n\n\nRESPONSE')
        # print(response['events'])

        for event in response['events']:
            if name in event['name']['text']:
                print(event['name'])
                events_res.append(event)
        # print('\n\n\nEVENT')
        # print(events_res)
        time.sleep(0.1)
    print(events_res)
    return events_res


def get_events_data(artist, city, distance):
    """Searches Eventbrite with artist name and location."""
    # TODO: fix request params by city as results aren't accurate
    # sometimes results yield "events"
    # sometimes yield "top_match_events"?

    # change input city to correct format
    city = '%20'.join(city.split())

    # FIXME: make sure artist is in the event name so random events don't show up
    query_params = {
        'q': artist,
        'location.address': city,
        'location.within': distance,
        'categories': '103',
        'expand': 'venue'
    }

    url_args = '&'.join([f"{key}={urllib.parse.quote(val)}" for key, val in query_params.items()])
    url = f"{EVENTBRITE_SEARCH_ENDPOINT}/?{url_args}"

    headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}
    response = requests.get(url, headers=headers)

    # handle invalid location error
    if response.status_code == 400:
        if response.json()['error_detail']['ARGUMENTS_ERROR']['location.address'][0] == 'INVALID':
            return "location invalid"
    elif response.status_code == 200:
        return response.json()


def search_batch_events(artist, city, distance):
    """Searches events with a batched request to the Eventbrite API."""

    city = '%20'.join(city.split())

    query_params1 = {
        'q': artist,
        'location.address': city,
        'location.within': distance,
        'categories': '103',
        'expand': 'venue'
    }

payload = [
            {"method":"GET", "relative_url":"/events/search?q=martin roth&location.address=san francisco&categories=103&expand=venue&location.within=15mi"},
            {"method":"GET", "relative_url":"/events/search?q=low steppa&location.address=san francisco&categories=103&expand=venue&location.within=15mi"}
            ]

headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}

response = requests.post(EVENTBRITE_BATCH_ENDPOINT, data=payload, headers=headers)
