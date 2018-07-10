from flask import Blueprint, request, jsonify, g
from bson import json_util
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import DecodeError, ExpiredSignature

JSON_MIME_TYPE = 'application/json'
TOKEN_TIMEOUT = 5 # time in minutes
JWT_ALGORITHM = 'HS256'
SECRET_KEY = 'super-secret'

bp = Blueprint('auth', __name__)

col_tokens = g.db.col_tokens
col_users = g.db.users


def jwt_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
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
		return f(*args, **kwargs)
	return decorated_function


def jwt_refresh_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
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
		return f(*args, **kwargs)
	return decorated_function


def create_access_token(user):
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
	payload = {
		'username': user['username'],
		'refresh': True,
		# issued at
		'iat': datetime.utcnow(),
	}
	token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
	return token.decode('unicode_escape')
	

def parse_token(req):
	token = req.headers.get('Authorization').split()[1]
	return jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM)


def authenticate(username, password):
    print(username)
    print(password)
    res = col_users.find({})

    print(json_util.dumps(list(res)))

    user = col_users.find_one({'username': username})
    print(user)
    if user and check_password_hash(user['password'], password):
        return user
    else:
        return None


@bp.route('/v1/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = authenticate(data['username'], data['password'])

    if user:
        token_payload = {'username': user['username']}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        col_tokens.insert_one({'value': refresh_token})
        response = json_util.dumps({'access_token': access_token, 
                                    'refresh_token': refresh_token})
        return response
    else:
        return "Unauthorized", 401


@bp.route('/refresh_token', methods=['GET'])
@jwt_refresh_required
def refresh_token():    
    token = col_tokens.find_one({'value': g.token})
    if token:
        col_tokens.delete_one({'value': g.token})
        token_payload = {'username': g.parsed_token['username']}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        col_tokens.insert_one({'value': refresh_token})
        return json_util.dumps({'access_token': access_token, 
                                'refresh_token': refresh_token}), 200
    else:
        return "Unauthorized", 401