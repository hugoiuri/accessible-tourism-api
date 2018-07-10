""" Flights API"""

# from flask import Blueprint, Response, request, g
from flask import Blueprint, Response, g
from bson import json_util
from api.auth import jwt_required

JSON_MIME_TYPE = 'application/json'

BP = Blueprint('fligths', __name__)

COL_FLIGHTS = g.db.fligths

@BP.route('/v1/flights', methods=['GET'])
@jwt_required
def get_all_flights():
    """ Get all flights """

    res = COL_FLIGHTS.find({})

    response = Response(
        json_util.dumps(list(res)), status=200, mimetype=JSON_MIME_TYPE)

    return response
