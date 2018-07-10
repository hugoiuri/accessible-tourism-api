""" Users API """

from flask import Blueprint, Response, request, g
from bson import json_util
from werkzeug.security import generate_password_hash
from api.auth import jwt_required

JSON_MIME_TYPE = 'application/json'

BP = Blueprint('users', __name__)

COL_USERS = g.db.users

@BP.route('/v1/users', methods=['GET'])
@jwt_required
def get_all_users():
    """ Get all users """

    res = COL_USERS.find({}, {'_id': 0, 'password': 0})

    response = Response(
        json_util.dumps(list(res)), status=200, mimetype=JSON_MIME_TYPE)

    return response


@BP.route('/v1/users', methods=['POST'])
@jwt_required
def insert_user():
    """ Insert same user """
    data = request.get_json()

    if 'password' not in data.keys() or 'username' not in data.keys():
        return 'Bad Request', 400

    username = data['username']
    user = COL_USERS.find_one({'username': username}, {'_id': 0, 'username': 1})

    if user is None:
        data['password'] = generate_password_hash(data['password'])
        COL_USERS.insert_one(data)
        return 'Usuário ' + data['username'] + ' criado', 201

    return 'Usuário ' + data['username'] + ' já existe', 409


@BP.route('/v1/users/<username>', methods=['GET'])
@jwt_required
def get_user(username):
    """ Get user by username """
    user = COL_USERS.find_one({'username': username}, {'_id': 0, 'password': 0})
    if user is None:
        return 'Usuário não encontrado', 404

    response = Response(json_util.dumps(user), status=200, mimetype=JSON_MIME_TYPE)
    return response
