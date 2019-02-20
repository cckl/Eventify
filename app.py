import os
from flask import Flask
from jinja2 import StrictUndefined

from config import FLASK_APP_KEY

app = Flask(__name__)
app.secret_key = 'FLASK_APP_KEY'
app.jinja_env.undefined = StrictUndefined
