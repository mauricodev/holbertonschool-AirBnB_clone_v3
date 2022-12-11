#!/usr/bin/python3
"""
Create routes:
    /cities/<city_id>/places:
        - GET: Returns all the Places of the city in JSON format.
        - POST: Submits a new Place to the city in JSON format.
        Returns the new Place.
    /places/<places_id>:
        - GET: Returns a Place by id in JSON format.
        - DELETE: Deletes a Place by id. Returns {} in success.
        - PUT: Modify a Place by id. Returns the modified Place.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.city import City
from models.place import Place
from models.user import User


@app_views.route("/places/<place_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def places_by_id(place_id):
    """GET/DELETE/PUT all the Places"""
    err = {
        "error": "Not found"
    }
    place = storage.get(Place, place_id)
    if place is None:
        return jsonify(err), 404
    if request.method == 'GET':
        return jsonify(place.to_dict())
    elif request.method == 'DELETE':
        storage.delete(place)
        storage.save()
        storage.reload()
        return jsonify({}), 200
    elif request.method == 'PUT':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        for k, v in request_data.items():
            if k == 'id' or k == 'created_at' or k == 'updated_at':
                continue
            setattr(place, k, v)
        storage.new(place)
        storage.save()
        storage.reload()
        return jsonify(place.to_dict()), 200


@app_views.route("/cities/<city_id>/places", methods=[
    'GET', 'POST'], strict_slashes=False)
def places_by_city(city_id):
    """GET/POST Place(s) by City"""
    err = {
        "error": "Not found"
    }
    city = storage.get(City, city_id)
    if city is None:
        return jsonify(err), 404
    if request.method == 'GET':
        json_data = []
        places = storage.all(Place)
        for place in places.values():
            if place.city_id == city_id:
                json_data.append(place.to_dict())
        return jsonify(json_data)
    elif request.method == 'POST':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        if 'user_id' not in request_data.keys():
            return 'Missing user_id', 400
        user = storage.get(User, request_data['user_id'])
        if user is None:
            return jsonify(err), 404
        if 'name' not in request_data.keys():
            return 'Missing name', 400
        place = Place(**request_data)
        place.city_id = city_id
        storage.new(place)
        storage.save()
        storage.reload()
        return jsonify(place.to_dict()), 201
