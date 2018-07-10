# """ Module for testing users API """

# import os
# import json
# import unittest
# from pymongo import MongoClient
# import api
# from config import MONGO_URI_TESTS

# class FligthsTestCase(unittest.TestCase):
#     """ Users unity test case """

#     def create_app(self):
#         """ Create a test app """
#         app = api.create_app(True)
#         self.client = app.test_client()


#     def get_token(self, user, password):
#         """ Generate a new token """
#         data = {'username': user, 'password': password}

#         response = self.client.post('/v1/signin',
#                                     data=json.dumps(data),
#                                     content_type='application/json')
#         response_data = json.loads(response.data)
#         return response_data['access_token']

#     def config_database(self):
#         """ Configure database test collections """
#         mongo_uri = os.getenv('MONGO_URI_TESTS', MONGO_URI_TESTS)
#         client = MongoClient(mongo_uri)
#         database = mongo_uri.split('/')[-1]
#         self.col_flights = client[database].flights
#         self.col_tokens = client[database].tokens


#     def database_cleanup(self):
#         """ Clear all database collections """
#         self.col_flights.delete_many({})
#         self.col_tokens.delete_many({})


#     def flights_populate(self):
#         """ Populate users collections """
#         test_flight = {
#             "company": "Latam",
#             "departureTime": "20:30",
#             "arrivalTime": "15:30",
#             "value": "550",
#             "currency": "BRL"
#         }
#         self.col_flights.insert_one(test_flight)


#     def populate(self):
#         """ Populate database for tests """
#         self.flights_populate()


#     def setUp(self):
#         """ Setup testd """
#         self.create_app()
#         self.config_database()
#         self.database_cleanup()
#         self.populate()
#         self.token = self.get_token('foo', '123')


#     def test_get_all_flights(self):
#         """ Should return all flighs in database """
#         response = self.client.get('/v1/flights',
#                                    headers={'Authorization': 'JWT ' + self.token},
#                                    content_type='application/json')

#         content = json.loads(response.get_data(as_text=True))

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(len(content), 1)
#         self.assertEqual(content, [{
#             "company": "Latam",
#             "departureTime": "20:30",
#             "arrivalTime": "15:30",
#             "value": "550",
#             "currency": "BRL"
#         }])


#     def tearDown(self):
#         # apagar todos documentos
#         self.database_cleanup()


# if __name__ == '__main__':
#     unittest.main()
