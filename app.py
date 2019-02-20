from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ['FLASK_APP_KEY']
app.jinja_env.undefined = StrictUndefined
