from flask import Blueprint, Response, request, json, g
from bson import json_util
from werkzeug.security import generate_password_hash
from api.auth import jwt_required

JSON_MIME_TYPE = 'application/json'

bp = Blueprint('users', __name__)

col_users = g.db.users

@bp.route('/v1/users', methods=['GET'])
@jwt_required
def get_all_users():
    """poc"""

    res = col_users.find({}, {'_id': 0, 'password': 0})

    response = Response(
        json_util.dumps(list(res)), status=200, mimetype=JSON_MIME_TYPE)

    return response


@bp.route('/v1/users', methods=['POST'])
@jwt_required
def insert_user():
    """ Insert same user """
    data = request.get_json()

    if 'password' not in data.keys() or 'username' not in data.keys():
        return 'Bad Request', 400

    username = data['username']
    
    user = col_users.find_one({'username': username}, {'_id': 0, 'username': 1})

    if user is None:
        data['password'] = generate_password_hash(data['password'])
        col_users.insert_one(data)
        return 'usuario ' + data['username'] + ' criado.', 201
    else:
        return 'usuario ' + data['username'] + ' já existe.', 409


@bp.route('/v1/users/<username>', methods=['GET'])
@jwt_required
def get_user(username):
    user = col_users.find_one({'username': username}, {'_id': 0, 'password': 0})
    if user == None: 
        return 'Usuário não encontrado', 404
    else:
        return json_util.dumps(user), 200
