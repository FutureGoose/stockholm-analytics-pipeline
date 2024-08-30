import unittest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import app

class TestMain(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/", params={"location": "London", "date": "2024-08-29"})
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("status_code", response.json())

if __name__ == "__main__":
    unittest.main()

# python pipes/weatherapi-api-weather-raw/tests/test_main.py