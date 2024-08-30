import unittest
from fastapi.testclient import TestClient
import os, sys
from unittest.mock import patch
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import app


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
        cls.client = TestClient(app)

    @patch('main.write')  # mock the write function
    def test_fetch_weather_data_endpoint(self, mock_write):
        mock_write.return_value = None  # mock the return value of the write function
        response = self.client.get("/", params={"location": "London", "date": "2024-08-29"})
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("status_code", response.json())
        self.assertEqual(response.json()["status_code"], 200)

if __name__ == "__main__":
    unittest.main()
