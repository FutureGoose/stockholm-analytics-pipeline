import unittest
from unittest.mock import patch, Mock
import pendulum
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import write


class TestWriteFunction(unittest.TestCase):

    def setUp(self):
        self.json_data = {
            "location": {"localtime": "2024-08-30 16:57"},
            "hour": [
                {"time_epoch": 1724882400, "temp_c": 15.0},
                {"time_epoch": 1724886000, "temp_c": 14.8}
            ]
        }

    def mock_bigquery_setup(self, mock_bigquery_client, insert_rows_return_value):
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows.return_value = insert_rows_return_value
        return mock_client_instance, mock_table

    @patch('main.bigquery.Client')
    def test_write_function(self, mock_bigquery_client):
        mock_client_instance, mock_table = self.mock_bigquery_setup(mock_bigquery_client, [])

        write(self.json_data)

        expected_rows = [
            {
                "ingestion_timestamp": pendulum.now().to_datetime_string(),
                "modified_timestamp": pendulum.from_format("2024-08-30 16:57", 'YYYY-MM-DD HH:mm').to_datetime_string(),
                "id": 1724882400,
                "data": json.dumps({"time_epoch": 1724882400, "temp_c": 15.0})
            },
            {
                "ingestion_timestamp": pendulum.now().to_datetime_string(),
                "modified_timestamp": pendulum.from_format("2024-08-30 16:57", 'YYYY-MM-DD HH:mm').to_datetime_string(),
                "id": 1724886000,
                "data": json.dumps({"time_epoch": 1724886000, "temp_c": 14.8})
            }
        ]

        mock_client_instance.insert_rows.assert_called_once_with(mock_table, expected_rows)

    @patch('main.bigquery.Client')
    def test_write_function_with_errors(self, mock_bigquery_client):
        mock_client_instance, mock_table = self.mock_bigquery_setup(mock_bigquery_client, ["Error inserting rows"])

        with self.assertRaises(Exception) as context:
            write(self.json_data)

        self.assertIn("Failed to insert rows", str(context.exception))

if __name__ == "__main__":
    unittest.main()
