#!/usr/bin/python3
"""
Create routes:
    /status: returns a JSON status response
"""
from api.v1.views import app_views
from flask import jsonify

@app_views.route("/status")
def show_status():
    """Returns the status of the HTTP request"""
    res = {
        "status": "OK"
    }
    return (jsonify(res))
