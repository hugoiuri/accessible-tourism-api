""" Auth API """

from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, json, g
from werkzeug.security import check_password_hash
import jwt
from jwt.exceptions import DecodeError, ExpiredSignature

JSON_MIME_TYPE = 'application/json'
TOKEN_TIMEOUT = 5 # time in minutes
JWT_ALGORITHM = 'HS256'
SECRET_KEY = 'super-secret'

BP = Blueprint('auth', __name__)

COL_TOKENS = g.db.col_tokens
COL_USERS = g.db.users


def jwt_required(func):
    """ Require JWT token """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """ Decorator function """
        if not request.headers.get('Authorization'):
            return jsonify(message='Missing authorization header'), 401
        try:
            payload = parse_token(request)
            if payload['refresh']:
                return jsonify('Token is not an access token.'), 401
            g.token = request.headers.get('Authorization').split()[1]
            g.parsed_token = payload
        except DecodeError:
            return jsonify(message='Token is invalid'), 401
        except ExpiredSignature:
            return jsonify(message='Token has expired'), 401
        return func(*args, **kwargs)
    return decorated_function


def jwt_refresh_required(func):
    """ Require refresh JWT token """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """ Decorator function """
        if not request.headers.get('Authorization'):
            return jsonify(message='Missing authorization header'), 401
        try:
            payload = parse_token(request)
            if not payload['refresh']:
                return jsonify('Token is not a refresh token.'), 401
            g.token = request.headers.get('Authorization').split()[1]
            g.parsed_token = payload
        except DecodeError:
            return jsonify(message='Token is invalid'), 401
        except ExpiredSignature:
            return jsonify(message='Token has expired'), 401
        return func(*args, **kwargs)
    return decorated_function


def create_access_token(user):
    """ Create JWT token """
    payload = {
        'username': user['username'],
        'refresh': False,
        # issued at
        'iat': datetime.utcnow(),
        # expiry
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_TIMEOUT)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token.decode('unicode_escape')


def create_refresh_token(user):
    """ Create refresh JWT token """
    payload = {
        'username': user['username'],
        'refresh': True,
        # issued at
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token.decode('unicode_escape')


def parse_token(req):
    """ decode JWT token """
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM)


def authenticate(username, password):
    """ Authenticate user by username and password """
    user = COL_USERS.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return user

    return None


@BP.route('/refresh_token', methods=['GET'])
@jwt_refresh_required
def refresh_token():
    """ Refrash JWT token """
    token = COL_TOKENS.find_one({'value': g.token})
    if token:
        COL_TOKENS.delete_one({'value': g.token})
        token_payload = {'username': g.parsed_token['username']}
        access_token = create_access_token(token_payload)
        rtoken = create_refresh_token(token_payload)
        COL_TOKENS.insert_one({'value': rtoken})
        return json.dumps({'access_token': access_token,
                           'refresh_token': rtoken}), 200

    return "Unauthorized", 401


@BP.route('/v1/signin', methods=['POST'])
def signin():
    """ Generate JWT for valid users """
    data = request.get_json()
    user = authenticate(data['username'], data['password'])

    if user:
        token_payload = {'username': user['username']}
        access_token = create_access_token(token_payload)
        rtoken = create_refresh_token(token_payload)
        COL_TOKENS.insert_one({'value': rtoken})
        response = json.dumps({'access_token': access_token,
                               'refresh_token': rtoken})
        return response

    return "Unauthorized", 401
