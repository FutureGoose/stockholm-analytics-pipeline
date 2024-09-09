import unittest
from fastapi.testclient import TestClient
import os 
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import read, app


class TestReadFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test client and load environment variables"""
        load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
        cls.client = TestClient(app)

    def test_read_function(self):
        """Test read function with sample data"""
        location = "Stockholm"
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        result = read(location, date)
        self.assertIn("location", result)
        self.assertIn("hour", result)
        self.assertIsInstance(result["hour"], list)

if __name__ == "__main__":
    unittest.main()