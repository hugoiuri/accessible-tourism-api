""" Acessible Tourism Service """

import os
import api


if __name__ == '__main__':
    APP = api.create_app()
    APP.debug = True
    HOST = os.environ.get('IP', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))
    APP.run(host=HOST, port=PORT)
