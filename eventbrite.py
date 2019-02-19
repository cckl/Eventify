"""Handles Eventbrite authorization and API requests."""

import os
import requests
import urllib # nit: requests should come after urllib.

# I'd probably extract these to a config or settings.py
# This will help with testability but also make the code a bit more focused on the implementation
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

    # This would be a good thing to extract to a function and then unit tested
    # This is another place where you ought to be careful for malicious inputs
    # is parse.quote generally robust for all inputs? (I'm not sure)
    url_args = '&'.join([f"{key}={urllib.parse.quote(val)}" for key, val in query_params.items()])
    url = f"{EVENTBRITE_SEARCH_ENDPOINT}/?{url_args}"
    
    # This can be extracted a function
    headers = {"Authorization": f"Bearer {EVENTBRITE_OAUTH_TOKEN}"}
    response = requests.get(url, headers=headers)

    # You should think about errors and at which part of your design should be repsonsible for handling errors
    return response.json()
