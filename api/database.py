from flask import current_app, g
from flask_pymongo import PyMongo

def get_db():
    if 'db' not in g:
        mongo = PyMongo(current_app)
        g.db = mongo.db

    return g.db
