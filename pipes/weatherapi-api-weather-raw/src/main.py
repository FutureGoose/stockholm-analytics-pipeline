import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
import pendulum

# initialize FastAPI
app = FastAPI()
# load environment variables
load_dotenv()


def fetch_weather_data(api_url: str, api_key: str, location: str, date: str) -> dict:
    """
    Fetches weather data from API.
    """
    params = {
        'key': api_key,
        'q': location,
        'date': date
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        print("Fetched data from API")
        return response.json()
    else:
        response.raise_for_status()


def write(json_data: dict) -> None:
    """
    Unpacks json and sends the data to BigQuery table.
    """
    client = bigquery.Client()
    table_id = "team-god.weather_data.raw_weatherapp"
    table = client.get_table(table_id)

    rows_to_insert = [
        {
            "ingestion_timestamp": pendulum.now().to_datetime_string(),
            "modified_timestamp": pendulum.from_format(json_data['location']['localtime'], 'YYYY-MM-DD HH:mm').to_datetime_string(),
            "id": hour['time_epoch'],
            "data": json.dumps(hour)
        }
        for hour in json_data['hour']
    ]

    errors = client.insert_rows(table, rows_to_insert)
    if errors:
        raise Exception(f"Failed to insert rows: {errors}")
    print(f'Inserted {len(rows_to_insert)} rows')


def read(location: str, date: str) -> dict:
    """
    Calls the API and formats the data for BigQuery.
    """
    API_URL = os.getenv('API_URL')
    API_KEY = os.getenv('API_KEY')

    if not API_URL or not API_KEY:
        raise HTTPException(status_code=500, detail="API_URL or API_KEY not set")

    try:
        weather_data = fetch_weather_data(
            api_url=API_URL,
            api_key=API_KEY,
            location=location,
            date=date
            )
        formatted_data = {
            'location': weather_data['location'],
            'hour': weather_data['forecast']['forecastday'][0]['hour']
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from API: {e}")

    return formatted_data
  

@app.get("/")
def main(location: str, date: str):
    # call read function to fetch data
    data = read(location, date)

    # call write function, send data to BigQuery
    try:
        data=write(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert to BigQuery failed: {e}")
    
    return {"status_code": 200}


# docker build -t gcr.io/team-god/weatherapi-api-weather-raw .
# docker push gcr.io/team-god/weatherapi-api-weather-raw
# gcloud auth configure-docker
# gcloud run deploy weatherapi-api-weather-raw-service --image gcr.io/team-god/weatherapi-api-weather-raw --platform managed --region europe-north1 --concurrency 2 --max-instances 2
# gcloud run services delete SERVICE_NAME --region europe-north1