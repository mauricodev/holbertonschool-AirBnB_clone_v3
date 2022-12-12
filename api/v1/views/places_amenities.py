#!/usr/bin/python3
"""
Create a new view for the link between Place objects and Amenity objects
that handles all default RESTFul API actions:
Routes:
    /places/<place_id>/amenities:
        - GET: Returns all the Amenities of a Place in JSON format.
    /places/<place_id>/amenities/<amenity_id>:
        - DELETE: Deletes an Amenity linked to a place by id.
                Returns {} in success.
        - POST: Submits an Amenity to a place in JSON format.
                Returns the Amenity.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage, storage_t
from models.place import Place
from models.amenity import Amenity


@app_views.route("/places/<place_id>/amenities", strict_slashes=False)
def amenities_by_place(place_id):
    """GET all Amenities by place"""
    err = {
        "error": "Not found"
    }
    place = storage.get(Place, place_id)
    if place is None:
        return jsonify(err), 404
    json_data = []
    if storage_t == 'db':
        for amenity in place.amenities:
            json_data.append(amenity.to_dict())
    else:
        for amenity_id in place.amenity_ids:
            amenity = storage.get(Amenity, amenity_id)
            json_data.append(amenity.to_dic())
    return jsonify(json_data)


@app_views.route(
    "/places/<place_id>/amenities/<amenity_id>", methods=[
        'DELETE', 'POST'], strict_slashes=False)
def amenity_in_place(place_id, amenity_id):
    """DELETE/POST Amenity in a Place"""
    err = {
        "error": "Not found"
    }
    place = storage.get(Place, place_id)
    if place is None:
        return jsonify(err), 404
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        return jsonify(err), 404

    if request.method == 'DELETE':
        if storage_t == 'db':
            if amenity not in place.amenities:
                return jsonify(err), 404
        else:
            if amenity.id not in place.amenity_ids:
                return jsonify(err), 404

        if storage_t == 'db':
            place.amenities.remove(amenity)
        else:
            place.amenity_ids.remove(amenity.id)
        storage.save()
        return jsonify({}), 200
    elif request.method == 'POST':
        if storage_t == 'db':
            if amenity in place.amenities:
                return jsonify(amenity.to_dict()), 200
        else:
            if amenity.id in place.amenity_ids:
                return jsonify(amenity.to_dict()), 200

        if storage_t == 'db':
            place.amenities.append(amenity)
        else:
            place.amenity_ids.append(amenity.id)
        storage.save()
        return jsonify(amenity.to_dict()), 201
