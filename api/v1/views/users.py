#!/usr/bin/python3
"""
Create routes:
    /users:
        - GET: Returns all the user in JSON format.
        - POST: Submits a User in JSON format. Returns the new User.
    /users/<user_id>:
        - GET: Returns a User by id in JSON format.
        - DELETE: Deletes a User by id. Returns {} in success.
        - PUT: Modify a User by id. Returns the modified User.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.user import User


@app_views.route("/users", methods=['GET', 'POST'], strict_slashes=False)
def users():
    """GET/POST all the Users"""
    if request.method == 'GET':
        users = storage.all(User)
        json_data = []
        for user in users.values():
            json_data.append(user.to_dict())
        return jsonify(json_data)
    elif request.method == 'POST':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        if 'email' not in request_data.keys():
            return 'Missing email', 400
        if 'password' not in request_data.keys():
            return 'Missing password', 400
        user = User(**request_data)
        storage.new(user)
        storage.save()
        storage.reload()
        return jsonify(user.to_dict()), 201


@app_views.route("/users/<user_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def users_by_id(user_id):
    """GET/DELETE/PUT a User by id"""
    err = {
        "error": "Not found"
    }
    if request.method == 'GET':
        user = storage.get(User, user_id)
        if user is None:
            return jsonify(err), 404
        return jsonify(user.to_dict()), 200
    elif request.method == 'DELETE':
        user = storage.get(User, user_id)
        if user is None:
            return jsonify(err), 404
        storage.delete(user)
        storage.save()
        storage.reload()
        return jsonify({}), 200
    elif request.method == 'PUT':
        user = storage.get(User, user_id)
        if user is None:
            return jsonify(err), 404
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        for k, v in request_data.items():
            if k == 'id' or k == 'email':
                continue
            if k == 'created_at' or k == 'updated_at':
                continue
            setattr(user, k, v)
        storage.new(user)
        storage.save()
        storage.reload()
        return jsonify(user.to_dict()), 200
