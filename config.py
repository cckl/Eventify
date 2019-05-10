import os

FLASK_APP_KEY=os.environ['FLASK_APP_KEY']

########################################
# Spotify client info and URI
SPOTIFY_CLIENT_ID=os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET=os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI='http://54.70.215.219/spotify-auth'

########################################
# Eventbrite client info and URLs
EVENTBRITE_APP_KEY = os.environ['EVENTBRITE_APP_KEY']
EVENTBRITE_CLIENT_SECRET=os.environ['EVENTBRITE_CLIENT_SECRET']
EVENTBRITE_OAUTH_TOKEN=os.environ['EVENTBRITE_OAUTH_TOKEN']
