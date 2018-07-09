import os
from flask import Flask
from config import MONGO_URI

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.update(test_config)

    app.config['MONGO_URI'] = MONGO_URI
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app_context = app.app_context()
    app_context.push() 

    # apply the blueprints to the app
    from api import users
    app.register_blueprint(users.bp)

    return app