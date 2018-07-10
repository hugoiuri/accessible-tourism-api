import os
import json
import unittest
import api
from config import MONGO_URI_TESTS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

class UsersTestCase(unittest.TestCase):
    
    def create_app(self):
        app = api.create_app(True)
        self.client = app.test_client()
    

    def get_token(self, user, password):
        data = {'username': user, 'password': password}
        
        response = self.client.post('/v1/signin', 
                                    data=json.dumps(data), 
                                    content_type='application/json')
        return response

    def config_database(self):
        client = MongoClient(MONGO_URI_TESTS)
        db = MONGO_URI_TESTS.split('/')[-1]        
        self.col_users = client[db].users
        self.col_tokens = client[db].tokens


    def database_cleanup(self):
        self.col_users.delete_many({})
        self.col_tokens.delete_many({})


    def user_populate(self):
        test_user = {'username': 'foo', 'password': generate_password_hash('123')}        
        self.col_users.insert_one(test_user)


    def token_populate(self):
        # Preenche o token de acesso para evitar a dependência entre os testes
        token_response = self.get_token('foo', '123')
        self.token = json.loads(token_response.data)['access_token']

    
    def populate(self):
        self.user_populate()
        self.token_populate()


    def setUp(self):
        self.create_app()
        self.config_database()
        self.database_cleanup()
        self.populate()


    def test_get_all_users(self):
        response = self.client.get('/v1/users',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json')

        content = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], {'username': 'foo'})


    def test_get_user(self):
        response = self.client.get('/v1/users/foo',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json')

        content = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(content, {'username': 'foo'})


    def test_get_not_exists_user(self):
        response = self.client.get('/v1/users/bar',
                                    headers={'Authorization': 'JWT ' + self.token},
                                    content_type='application/json')

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário não encontrado')
    

    def test_create_user(self):
        data = {'username': 'baz', 'password': '123'}

        response = self.client.post('/v1/users',
                                     headers={'Authorization': 'JWT ' + self.token},
                                     content_type='application/json',
                                     data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário baz criado')
    

    def test_create_user_without_username(self):
        data = {'email': 'baz@email.com', 'password': '123'}

        response = self.client.post('/v1/users',
                                     headers={'Authorization': 'JWT ' + self.token},
                                     content_type='application/json',
                                     data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Bad Request')
    

    def test_create_user_without_password(self):
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
        data = {'username': 'foo', 'password': '123'}

        response = self.client.post('/v1/users',
                                     headers={'Authorization': 'JWT ' + self.token},
                                     content_type='application/json',
                                     data=json.dumps(data))

        content = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertEqual(content, 'Usuário foo já existe')