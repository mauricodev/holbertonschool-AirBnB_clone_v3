#!/usr/bin/python3
"""
Create routes:
    /states:
        - GET: Returns all the states in JSON format.
        - POST: Submits a state in JSON format. Returns the new State.
    /states/<state_id>: returns the number of each objects by type
        - GET: Returns a state by id in JSON format.
        - DELETE: Deletes a State by id. Returns {} in success.
        - PUT: Modify a state by id. Returns the modified State.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.state import State


@app_views.route("/states", methods=['GET', 'POST'], strict_slashes=False)
def states():
    """GET/POST all the States"""
    if request.method == 'GET':
        states = storage.all(State)
        json_data = []
        for state in states.values():
            json_data.append(state.to_dict())
        return jsonify(json_data)
    elif request.method == 'POST':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400
        elif 'name' not in request_data.keys():
            return 'Missing name', 400

        state = State(**request_data)
        storage.new(state)
        storage.save()
        storage.reload()
        return jsonify(state.to_dict()), 201


@app_views.route("/states/<state_id>", methods=[
    'GET', 'DELETE', 'PUT'], strict_slashes=False)
def states_by_id(state_id):
    """GET/DELETE/PUT a State by id"""
    states = storage.all(State)
    err = {
        "error": "Not found"
    }
    if request.method == 'GET':
        for state in states.values():
            if state.id == state_id:
                return jsonify(state.to_dict())
        return jsonify(err), 404
    elif request.method == 'DELETE':
        for state in states.values():
            if state.id == state_id:
                state = storage.get(State, state_id)
                storage.delete(state)
                storage.save()
                storage.reload()
                return jsonify({}), 200
        return jsonify(err), 404
    elif request.method == 'PUT':
        for state in states.values():
            if state.id == state_id:
                request_data = request.get_json(silent=True)
                if request_data is None or not isinstance(request_data, dict):
                    return 'Not a JSON', 400
                state = storage.get(State, state_id)
                for k, v in request_data.items():
                    if k == 'id' or k == 'created_at' or k == 'updated_at':
                        continue
                    setattr(state, k, v)
                storage.new(state)
                storage.save()
                storage.reload()
                return jsonify(state.to_dict()), 200
        return jsonify(err), 404
