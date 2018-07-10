""" Module for testing users API """

import os
import json
import unittest
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import api
from config import MONGO_URI_TESTS

class UsersTestCase(unittest.TestCase):
    """ Users unity test case """

    def create_app(self):
        """ Create a test app """
        app = api.create_app(True)
        self.client = app.test_client()


    def get_token(self, user, password):
        """ Generate a new token """
        data = {'username': user, 'password': password}

        response = self.client.post('/v1/signin',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response_data = json.loads(response.data)
        return response_data['access_token']

    def config_database(self):
        """ Configure database test collections """
        mongo_uri = os.getenv('MONGO_URI_TESTS', MONGO_URI_TESTS)
        client = MongoClient(mongo_uri)
        database = mongo_uri.split('/')[-1]
        self.col_users = client[database].users
        self.col_tokens = client[database].tokens


    def database_cleanup(self):
        """ Clear all database collections """
        self.col_users.delete_many({})
        self.col_tokens.delete_many({})


    def user_populate(self):
        """ Populate users collections """
        test_user = {'username': 'foo', 'password': generate_password_hash('123')}
        self.col_users.insert_one(test_user)


    def populate(self):
        """ Populate database for tests """
        self.user_populate()


    def setUp(self):
        """ Setup testd """
        self.create_app()
        self.config_database()
        self.database_cleanup()
        self.populate()
        self.token = self.get_token('foo', '123')


    def test_get_all_users(self):
        """ Should return all users in database """
        response = self.client.get('/v1/users',
                                   headers={'Authorization': 'JWT ' + self.token},
                                   content_type='application/json')

        content = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(content), 1)
        self.assertEqual(content, [{'username': 'foo'}])


    def test_get_user(self):
        """ Should return a user by name """
        response = self.client.get('/v1/users/foo',
                                   headers={'Authorization': 'JWT ' + self.token},
                                   content_type='application/json')

        content = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(content, {'username': 'foo'})


    def test_get_not_exists_user(self):
        """ Should return 404 for a invalid username """
        response = self.client.get('/v1/users/bar',
                                   headers={'Authorization': 'JWT ' + self.token},
                                   content_type='application/json')

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário não encontrado')


    def test_create_user(self):
        """ Should create a user and return 201 """
        data = {'username': 'baz', 'password': '123'}

        response = self.client.post('/v1/users',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json',
                                    data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário baz criado')


    def test_without_username(self):
        """ Should return bad request (400) when does not pass username """
        data = {'email': 'baz@email.com', 'password': '123'}

        response = self.client.post('/v1/users',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json',
                                    data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Bad Request')


    def test_without_password(self):
        """ Should return bad request (400) when does not pass password """
        data = {'username': 'baz'}

        response = self.client.post('/v1/users',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json',
                                    data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Bad Request')


    def test_create_existing_user(self):
        """ Should return (409) when user alredy exist """
        data = {'username': 'foo', 'password': '123'}

        response = self.client.post('/v1/users',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json',
                                    data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário foo já existe')


    def tearDown(self):
        # apagar todos documentos
        self.database_cleanup()


if __name__ == '__main__':
    unittest.main()
