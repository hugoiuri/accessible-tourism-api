from flask import Blueprint, Response, current_app, json
from flask_pymongo import PyMongo
from bson import json_util


JSON_MIME_TYPE = 'application/json'

bp = Blueprint('users', __name__)

print(current_app.config['MONGO_URI'])
mongo = PyMongo(current_app)

col_users = mongo.db.users

@bp.route('/v1/users')
def index():
    """poc"""

    res = col_users.find({})

    response = Response(
        json_util.dumps(list(res)), status=200, mimetype=JSON_MIME_TYPE)

    return response
