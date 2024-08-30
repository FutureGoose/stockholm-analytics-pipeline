import unittest
from fastapi.testclient import TestClient
import os, sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import read, app


class TestReadFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
        cls.client = TestClient(app)

    def test_read_function(self):
        location = "Stockholm"
        date = "2024-08-29"
        result = read(location, date)
        print(result)
        self.assertIn("location", result)
        self.assertIn("hour", result)
        self.assertIsInstance(result["hour"], list)

if __name__ == "__main__":
    unittest.main()