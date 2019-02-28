"""Handles Eventbrite authorization and API requests."""

from datetime import datetime
import json
import os
import urllib
import re
import requests

from config import EVENTBRITE_APP_KEY, EVENTBRITE_CLIENT_SECRET, EVENTBRITE_OAUTH_TOKEN

EVENTBRITE_SEARCH_ENDPOINT='https://www.eventbriteapi.com/v3/events/search'
EVENTBRITE_BATCH_ENDPOINT='https://www.eventbriteapi.com/v3/batch/'


def search_batch_events(artists, city, distance):
    """Searches events with a batched request to the Eventbrite API."""

    req_payload = []

    # creates URLs to add to the batched request
    for artist in artists:
        name = artist[1]
        query_params = {
            'q': name,
            'location.address': city,
            'location.within': distance,
            'categories': '103',
            'expand': 'venue'
        }
        url_args = urllib.parse.urlencode(query_params)
        url = f"/events/search?{url_args}"
        print('THIS IS THE URL')
        print(url)
        req = {'method': 'GET', 'relative_url': url}
        req_payload.append(req)

    # converts batch to JSON for post request
    req_payload = json.dumps(req_payload)
    batch = {"batch": req_payload}
    headers = {'Authorization': f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}
    response = requests.post(EVENTBRITE_BATCH_ENDPOINT, data=batch, headers=headers)

    # handling of invalid location input
    if response.status_code == 400:
        if response.json()['error_detail']['ARGUMENTS_ERROR']['location.address'][0] == 'INVALID':
            return "location invalid"
    elif response.status_code == 200:
        results = []
        response = response.json()
        filtered_events = filter_events(artists, response)
        if filtered_events:
            formatted_events = format_batch_events(filtered_events)
            results.extend(formatted_events)
            return results


def filter_events(artists, response):
    """Decodes JSON and filters Eventbrite event data for events with artist name in the title."""

    initial_matches = []
    filtered_events = []

    for r in response:
        decoded_events = json.loads(r['body'])
        if decoded_events['events']:
            for event in decoded_events['events']:
                initial_matches.append(event)

    for match in initial_matches:
        for artist in artists:
            name = artist[1].lower()
            title = match['name']['text'].lower()
            # use regex to accurately check for name match in title
            if re.search(r'\b{}(?!\w|[?\'.,!])\b'.format(name), title):
                filtered_events.append(match)
            # if name.lower() in match['name']['text'].lower():
            #     filtered_events.append(match)

    return filtered_events


def format_batch_events(filtered_events):
    """Formats JSON data to store only necessary information."""

    formatted_events = []

    for event in filtered_events:
        address = f"{event['venue']['address']['address_1']}, {event['venue']['address']['city']}, {event['venue']['address']['region']}, {event['venue']['address']['postal_code']}"
        iso_starts_at = event['start']['utc']
        iso_ends_at = event['end']['utc']

        # https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime-with-python
        # https://docs.python.org/2/library/datetime.html
        formatted_event = {
            'name': event['name']['text'],
            'description': event['description']['text'],
            'starts_at': datetime.strptime(iso_starts_at, '%Y-%m-%dT%H:%M:%SZ'),
            'ends_at': datetime.strptime(iso_ends_at, '%Y-%m-%dT%H:%M:%SZ'),
            'venue': event['venue']['name'],
            'address': address,
            'url': event['url'],
            'img': event['logo']['original']['url']
            }
        formatted_events.append(formatted_event)

    return formatted_events
