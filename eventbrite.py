"""Handles Eventbrite authorization and API requests."""

import os
import urllib
import requests
from datetime import datetime
from config import EVENTBRITE_APP_KEY, EVENTBRITE_CLIENT_SECRET, EVENTBRITE_OAUTH_TOKEN

EVENTBRITE_SEARCH_ENDPOINT='https://www.eventbriteapi.com/v3/events/search'
EVENTBRITE_BATCH_ENDPOINT='https://www.eventbriteapi.com/v3/batch'

def get_events(artists, city, distance):
    """Search for events given a list of top 40 Spotify artists."""

    results = []

    for artist in artists:
        name = artist[1]

        city = '%20'.join(city.split())

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

        # check for error in response client_encoded_str
        # can extract to another function
        if response.status_code == 400:
            if response.json()['error_detail']['ARGUMENTS_ERROR']['location.address'][0] == 'INVALID':
                return "location invalid"
        elif response.status_code == 200:
            response = response.json()

            # FIXME: there's no way of knowing that an event is relevant,
            # aka the artist name is in the title until i filter the events.
            # guess i have no choice but to call the function every time to check?
            filtered_events = filter_events(name, response)
            if filtered_events:
                formatted_events = format_events(filtered_events)
                results.extend(formatted_events)

    return results


def filter_events(name, response):
    """Filter Eventbrite event data for events with artist name in the title."""

    filtered_events = [event for event in response['events'] if name in event['name']['text']]

    print(filtered_events)
    return filtered_events


def format_events(filtered_events):
    """Formats JSON data to store only necessary information."""

    formatted_events = []

    for event in filtered_events:
        address = f"{event['venue']['address']['address_1']}, {event['venue']['address']['city'] }, {event['venue']['address']['region']}, {event['venue']['address']['postal_code']}"
        iso_starts_at = event['start']['local']
        iso_ends_at = event['end']['local']

        formatted_event = {
            'name': event['name']['text'],
            'description': event['description']['text'],
            'starts_at': datetime.strptime(iso_starts_at, '%Y-%m-%dT%H:%M:%S'),
            'ends_at': datetime.strptime(iso_ends_at, '%Y-%m-%dT%H:%M:%S'),
            'venue': event['venue']['name'],
            'address': address,
            'url': event['url'],
            'img': event['logo']['original']['url']
            }

        formatted_events.append(formatted_event)
        print(formatted_event)

    print(formatted_events)
    return formatted_events


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

    # needs to be json encoded
    # json.dumps()
    # think of python as a 'superset' of json
    payload = [
                {"method":"GET", "relative_url":"/events/search?q=martin roth&location.address=san francisco&categories=103&expand=venue&location.within=15mi"},
                {"method":"GET", "relative_url":"/events/search?q=low steppa&location.address=san francisco&categories=103&expand=venue&location.within=15mi"}
                ]

    headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}

    response = requests.post(EVENTBRITE_BATCH_ENDPOINT, data=payload, headers=headers)
