"""Handles Eventbrite authorization and API requests."""

import os
import requests
import urllib

EVENTBRITE_APP_KEY = os.environ['EVENTBRITE_APP_KEY']
EVENTBRITE_CLIENT_SECRET=os.environ['EVENTBRITE_CLIENT_SECRET']
EVENTBRITE_OAUTH_TOKEN=os.environ['EVENTBRITE_OAUTH_TOKEN']
EVENTBRITE_SEARCH_ENDPOINT='https://www.eventbriteapi.com/v3/events/search'

def get_events_data(artist, city):
    """Searches Eventbrite with artist name and location."""
    # need to fix request params by city as results aren't accurate
    # sometimes results yield "events"
    # sometimes yield "top_match_events"?

    query_params = {
        'q': artist,
        'location.address': city,
        'categories': '103',
        'expand': 'venue'
    }

    url_args = '&'.join([f"{key}={urllib.parse.quote(val)}" for key, val in query_params.items()])
    url = f"{EVENTBRITE_SEARCH_ENDPOINT}/?{url_args}"
    
    headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}
    response = requests.get(url, headers=headers)

    return response.json()
