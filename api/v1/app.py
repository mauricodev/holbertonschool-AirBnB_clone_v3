#!/usr/bin/python3
"""
Starts a Flask web application with blueprint
"""
from flask import Flask, jsonify
from flask_cors import CORS
from models import storage
from api.v1.views import app_views
from os import getenv

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, origins="0.0.0.0")


@app.errorhandler(404)
def error404(e):
    res = {
        "error": "Not found"
    }
    return (jsonify(res)), 404


@app.teardown_appcontext
def teardown_db(exc):
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
