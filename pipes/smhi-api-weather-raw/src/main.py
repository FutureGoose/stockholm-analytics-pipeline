import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import psycopg2
import pendulum
from google.cloud import bigquery

app = FastAPI()
load_dotenv()

def fetch_radiation_data(api_url: str, longitude: str, latitude: str, parameter: str, from_date: str, to_date: str) -> dict:
    """
    Fetches radiation data from API.
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    
    full_url = f"{api_url}/lon/{longitude}/lat/{latitude}/parameter/{parameter}/data.json"
    
    try:
        response = requests.get(full_url, params=params)
        response.raise_for_status()
        print("Fetched data from API")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def write_to_bigquery(json_data: dict, parameter: int) -> None:
    """
    Sends fetched data to BigQuery table.
    """
    client = bigquery.Client()
    table_id = "team-god.radiation_data.raw_radiation_app"
    table = client.get_table(table_id)

    rows_to_insert = [
        {
            "ingestion_timestamp": pendulum.now().to_datetime_string(),
            "parameter": parameter,
            "data": json.dumps(record)
        }
        for record in json_data
    ]

    errors = client.insert_rows(table, rows_to_insert)
    if errors:
        raise Exception(f"Failed to insert rows: {errors}")
    print(f'Inserted {len(rows_to_insert)} rows for parameter {parameter}')


def read_and_write_radiation_data(api_url: str, longitude: float, latitude: float) -> None:
    """
    Fetches data for six radiation parameters and writes them to BigQuery.
    """
    # Define the six parameters to fetch
    parameters = [116, 117, 118, 120, 121, 122]
    
    # Get the current date and calculate the date range (from day before yesterday to yesterday)
    to_date = pendulum.yesterday().to_date_string()
    from_date = pendulum.yesterday().subtract(days=1).to_date_string()

    # Loop through each parameter, fetch data, and write to BigQuery
    for parameter in parameters:
        print(f"Fetching data for parameter {parameter}...")
        data = fetch_radiation_data(api_url, longitude, latitude, parameter, from_date, to_date)
        
        if data:
            print(f"Writing data for parameter {parameter} to BigQuery...")
            write_to_bigquery(data, parameter)
        else:
            print(f"No data fetched for parameter {parameter}.")


@app.get("/")
def main():
    # Set up API URL and location details
    API_URL = os.getenv('API_URL') or "https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point"
    # Longitude and latitude for Stockholm
    longitude = 18.0649
    latitude = 59.33258

    try:
        # Call the function to fetch and write radiation data for all six parameters
        read_and_write_radiation_data(api_url=API_URL, longitude=longitude, latitude=latitude)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {e}")
    
    return {"status_code": 200, "message": "Data fetched and stored in BigQuery successfully"}



# docker build -t gcr.io/team-god/smhi-api-weather-raw .
# docker push gcr.io/team-god/smhi-api-weather-raw
# gcloud auth configure-docker
# gcloud run deploy smhi-api-weather-raw-service --image gcr.io/team-god/smhi-api-weather-raw --platform managed --region europe-north1 --concurrency 2 --max-instances 2
# gcloud run services delete SERVICE_NAME --region europe-north1