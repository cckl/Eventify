"""Handles Eventbrite authorization and API requests."""

import os
import requests

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

    headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}

    url = EVENTBRITE_SEARCH_ENDPOINT + '?q=' + query_params['q'] + '&location.address=' + query_params['location.address'] + '&categories=103&expand=venue'

    response = requests.get(url, headers=headers)

    return response.json()
