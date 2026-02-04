# passenger_wsgi.py
# Change "app" to the module that creates your Flask app if different.
# If your main file is "app.py" and it contains "app = Flask(__name__)",
# this will work.
from app import app as application
