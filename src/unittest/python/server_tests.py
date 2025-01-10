import unittest
from server import app

class TestFlaskApp(unittest.TestCase):
    print("Running test...")

    def setUp(self):
        self.client = app.test_client()

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

