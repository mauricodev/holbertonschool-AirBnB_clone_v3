#!/usr/bin/python3
"""
Create routes:
    /states/<state_id>/cities:
        - GET: Returns all the cities of the state in JSON format.
        - POST: Submits a new city to the state in JSON format.
        Returns the new State.
    /cities/<city_id>:
        - GET: Returns a city by id in JSON format.
        - DELETE: Deletes a City by id. Returns {} in success.
        - PUT: Modify a city by id. Returns the modified City.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.state import State
from models.city import City


@app_views.route("/cities/<city_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def cities_by_id(city_id):
    """GET/DELETE/PUT all the Cities"""
    err = {
        "error": "Not found"
    }
    if request.method == 'GET':
        city = storage.get(City, city_id)
        if city is None:
            return jsonify(err), 404
        return jsonify(city.to_dict())
    elif request.method == 'DELETE':
        city = storage.get(City, city_id)
        if city is None:
            return jsonify(err), 404
        storage.delete(city)
        storage.save()
        storage.reload()
        return jsonify({}), 200
    elif request.method == 'PUT':
        city = storage.get(City, city_id)
        if city is None:
            return jsonify(err), 404
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        for k, v in request_data.items():
            if k == 'id' or k == 'created_at' or k == 'updated_at':
                continue
            setattr(city, k, v)
        storage.new(city)
        storage.save()
        storage.reload()
        return jsonify(city.to_dict()), 200


@app_views.route("/states/<state_id>/cities", methods=[
    'GET', 'POST'], strict_slashes=False)
def cities_by_state(state_id):
    """GET/POST Cities/City by State"""
    err = {
        "error": "Not found"
    }
    if request.method == 'GET':
        state = storage.get(State, state_id)
        if state is None:
            return jsonify(err), 404
        json_data = []
        for city in state.cities:
            json_data.append(city.to_dict())
        return jsonify(json_data)
    elif request.method == 'POST':
        state = storage.get(State, state_id)
        if state is None:
            return jsonify(err), 404
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        elif 'name' not in request_data.keys():
            return 'Missing name', 400
        city = City(**request_data)
        city.state_id = state_id
        storage.new(city)
        storage.save()
        storage.reload()
        return jsonify(city.to_dict()), 201
