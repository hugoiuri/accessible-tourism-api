""" Flights API"""

from flask import Blueprint, Response, request, g
from bson import json_util
from api.auth import jwt_required

JSON_MIME_TYPE = 'application/json'

BP = Blueprint('flights', __name__)

COL_FLIGHTS = g.db.flights


@BP.route('/v1/flights', methods=['GET'])
@jwt_required
def get_all_flights():
    """ Get all flights """
    response = None
    args = request.args.to_dict()

    if len(args) is 0:
        res = COL_FLIGHTS.find()
        flights = json_util.dumps(list(res))

        response = Response(
            flights, status=200, mimetype=JSON_MIME_TYPE)
    else:
        res = COL_FLIGHTS.find({'departure': args['departure'],
                                'arrival': args['arrival']})
        flights = json_util.dumps(list(res))

        response = Response(
            flights, status=200, mimetype=JSON_MIME_TYPE)

    return response
