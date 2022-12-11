#!/usr/bin/python3
"""
Create routes:
    /places/<place_id>/reviews:
        - GET: Returns all the Review of a place in JSON format.
        - POST: Submits a new Review for a place in JSON format.
        Returns the new Review.
    /reviews/<review_id>:
        - GET: Returns a Review by id in JSON format.
        - DELETE: Deletes a Review by id. Returns {} in success.
        - PUT: Modify a Review by id. Returns the modified Review.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.place import Place
from models.review import Review
from models.city import City
from models.user import User


@app_views.route("/reviews/<review_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def review_by_id(review_id):
    """GET/DELETE/PUT a Review by id"""
    err = {
        "error": "Not found"
    }
    review = storage.get(Review, review_id)
    if review is None:
        return jsonify(err), 404
    if request.method == 'GET':
        return jsonify(review.to_dict())
    elif request.method == 'DELETE':
        storage.delete(review)
        storage.save()
        storage.reload()
        return jsonify({}), 200
    elif request.method == 'PUT':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        for k, v in request_data.items():
            if k == 'id' or k == 'user_id' or k == 'place_id':
                continue
            if k == 'created_at' or k == 'updated_at':
                continue
            setattr(review, k, v)
        storage.new(review)
        storage.save()
        storage.reload()
        return jsonify(review.to_dict()), 200


@app_views.route("/places/<place_id>/reviews", methods=[
    'GET', 'POST'], strict_slashes=False)
def reviews_by_place(place_id):
    """GET all Reviews by place or POST a new Review"""
    err = {
        "error": "Not found"
    }
    place = storage.get(Place, place_id)
    if place is None:
        return jsonify(err), 404
    if request.method == 'GET':
        json_data = []
        reviews = storage.all(Review)
        for review in reviews.values():
            if review.place_id == place_id:
                json_data.append(review.to_dict())
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
        if 'text' not in request_data.keys():
            return 'Missing text', 400
        review = Review(**request_data)
        review.place_id = place_id
        storage.new(review)
        storage.save()
        storage.reload()
        return jsonify(review.to_dict()), 201
