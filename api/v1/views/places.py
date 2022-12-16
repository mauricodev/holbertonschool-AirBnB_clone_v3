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
    /places_search:
        - POST: Post parameters to get places accorded to parameters.
"""
from api.v1.views import app_views
from flask import jsonify, request
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.state import State
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
            if k == 'id' or k == 'user_id' or k == 'city_id':
                continue
            if k == 'created_at' or k == 'updated_at':
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


@app_views.route("/places_search", methods=['POST'], strict_slashes=False)
def places_search():
    """POST search parameters to get places founded."""
    if request.method == 'POST':
        request_data = request.get_json(silent=True)
        if request_data is None or not isinstance(request_data, dict):
            return 'Not a JSON', 400

        places = storage.all(Place)
        all_places = []
        keys_are_empty = True
        for place in places.values():
            all_places.append(place.to_dict())
        if request_data == {}:
            return jsonify(all_places)
        for v in request_data.values():
            if len(v) > 0:
                keys_are_empty = False
                break
        if keys_are_empty:
            return jsonify(all_places)

        st_exists = ct_exists = False
        st_empty = ct_empty = False
        if 'states' in request_data:
            st_exists = True
            if len(request_data['states']) == 0:
                st_empty = True
        if 'cities' in request_data:
            ct_exists = True
            if len(request_data['cities']) == 0:
                ct_empty = True

        result = []
        if st_exists and ct_exists:
            if st_empty and ct_empty:
                result = all_places
        else:
            result = all_places

        cities_id = []
        if 'states' in request_data:
            if len(request_data['states']) > 0:
                for st_id in request_data['states']:
                    state = storage.get(State, st_id)
                    for city in state.cities:
                        cities_id.append(city.id)
                    for ct_id in cities_id:
                        for place in places.values():
                            if place.city_id == ct_id:
                                result.append(place.to_dict())

        if 'cities' in request_data:
            if len(request_data['cities']) > 0:
                for ct_id in request_data['cities']:
                    if ct_id in cities_id:
                        continue
                    for place in places.values():
                        if place.city_id == ct_id:
                            result.append(place.to_dict())

        if 'amenities' in request_data:
            if len(request_data['amenities']) > 0:
                items_to_delete = []
                for pl in result:
                    amenities_ids = []
                    place = storage.get(Place, pl.get("id"))
                    if storage_t == 'db':
                        for amenity in place.amenities:
                            amenities_ids.append(amenity.id)
                    else:
                        for amenity_id in place.amenity_ids:
                            amenities_ids.append(amenity_id)
                    have_all_amenities = True
                    for am_id in request_data['amenities']:
                        if am_id not in amenities_ids:
                            have_all_amenities = False
                            break
                    if not have_all_amenities:
                        items_to_delete.append(pl)
                for item in items_to_delete:
                    result.remove(item)
        return jsonify(result)
