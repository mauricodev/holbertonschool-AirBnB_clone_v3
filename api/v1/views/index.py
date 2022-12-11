#!/usr/bin/python3
"""
Create routes:
    /status: returns a JSON status response
    /stats: returns the number of each objects by type
"""
from api.v1.views import app_views
from flask import jsonify
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

@app_views.route("/status")
def show_status():
    """Returns the status of the HTTP request"""
    res = {
        "status": "OK"
    }
    return (jsonify(res))


@app_views.route("/stats")
def show_stats():
    """Returns the number of each objects by type"""
    res = {
        "amenities": storage.count(Amenity),
        "cities": storage.count(City),
        "places": storage.count(Place),
        "reviews": storage.count(Review),
        "states": storage.count(State),
        "users": storage.count(User)
    }
    return (jsonify(res))
