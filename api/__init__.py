""" Acessible Tourism API """
import os
from flask import Flask
from config import MONGO_URI, MONGO_URI_TESTS


def create_app(test_config=None):
    """ Create and configure an instance of the Flask application """
    app = Flask(__name__)

    if test_config is None:
        app.config['MONGO_URI'] = os.getenv('MONGO_URI', MONGO_URI)
    else:
        app.config['MONGO_URI'] = os.getenv('MONGO_URI_TESTS', MONGO_URI_TESTS)


    # app.config['MONGO_URI'] = MONGO_URI
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app_context = app.app_context()
    app_context.push()

    # initialize database
    from api import database
    database.get_db()

    # apply the blueprints to the app
    from api import auth
    app.register_blueprint(auth.BP)
    from api import users
    app.register_blueprint(users.BP)

    return app
