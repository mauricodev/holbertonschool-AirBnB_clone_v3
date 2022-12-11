#!/usr/bin/python3
"""
Starts a Flask web application with blueprint
"""
from flask import Flask
from models import storage
from api.v1.views import app_views
from os import getenv

app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown_db(exception):
    """closes the storage on teardown"""
    storage.close()


if __name__ == "__main__":
    ip = getenv("HBNB_API_HOST")
    port = getenv("HBNB_API_PORT")

    if ip is None: 
        ip = '0.0.0.0'
    if port is None: 
        port = '5000'

    app.run(host=ip, port=port, threaded=True)
