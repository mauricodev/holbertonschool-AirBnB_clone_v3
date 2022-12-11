#!/usr/bin/python3
"""
Create routes:
    /amenities:
        - GET: Returns all the amenities in JSON format.
        - POST: Submits a state in JSON format. Returns the new State.
    /amenities/<amenity_id>: returns the number of each objects by type
        - GET: Returns a state by id in JSON format.
        - DELETE: Deletes a State by id. Returns {} in success.
        - PUT: Modify a state by id. Returns the modified State.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.amenity import Amenity


@app_views.route("/amenities", methods=['GET', 'POST'], strict_slashes=False)
def amenities():
    """GET/POST all the Amenities"""
    if request.method == 'GET':
        amenities = storage.all(Amenity)
        json_data = []
        for amenity in amenities.values():
            json_data.append(amenity.to_dict())
        return jsonify(json_data)
    elif request.method == 'POST':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        elif 'name' not in request_data.keys():
            return 'Missing name', 400
        amenity = Amenity(**request_data)
        storage.new(amenity)
        storage.save()
        storage.reload()
        return jsonify(amenity.to_dict()), 201


@app_views.route("/amenities/<amenity_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def amenities_by_id(amenity_id):
    """GET/DELETE/PUT a Amenity by id"""
    err = {
        "error": "Not found"
    }
    if request.method == 'GET':
        amenity = storage.get(Amenity, amenity_id)
        if amenity is None:
            return jsonify(err), 404
        return jsonify(amenity.to_dict())
    elif request.method == 'DELETE':
        amenity = storage.get(Amenity, amenity_id)
        if amenity is None:
            return jsonify(err), 404
        storage.delete(amenity)
        storage.save()
        storage.reload()
        return jsonify({}), 200
    elif request.method == 'PUT':
        amenity = storage.get(Amenity, amenity_id)
        if amenity is None:
            return jsonify(err), 404
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        for k, v in request_data.items():
            if k == 'id' or k == 'created_at' or k == 'updated_at':
                continue
            setattr(amenity, k, v)
        storage.new(amenity)
        storage.save()
        storage.reload()
        return jsonify(amenity.to_dict()), 200
