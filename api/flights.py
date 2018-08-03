""" Flights API"""

from flask import Blueprint, Response, request, g
from bson import json_util
from api.auth import jwt_required

JSON_MIME_TYPE = 'application/json'

BP = Blueprint('flights', __name__)

COL_FLIGHTS = g.db.flights


def get_all_flights():
    """ Get all flights """
    res = COL_FLIGHTS.find()
    flights = json_util.dumps(list(res))
    return flights


def search_flights():
    """ Search flights by filter """
    res = COL_FLIGHTS.find().limit(10)
    flights = json_util.dumps(list(res))

    return flights

@BP.route('/v1/flights', methods=['GET'])
@jwt_required
def get_flights():
    """ Get flights """
    response = None
    args = request.args.to_dict()

    if len(args) is 0:
        flights = get_all_flights()
        response = Response(flights, status=200, mimetype=JSON_MIME_TYPE)
    else:
        flights = search_flights()

        response = Response(
            flights, status=200, mimetype=JSON_MIME_TYPE)

    return response
