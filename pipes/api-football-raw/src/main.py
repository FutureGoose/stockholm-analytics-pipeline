import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
import pendulum
import time

# initialize FastAPI
app = FastAPI()
# load environment variables
load_dotenv()

def fetch_data(endpoint: str, api_key: str, params: dict) -> dict:
    """
    Fetches data from the API using the base URL from environment variables.
    """
    api_url = os.getenv('API_URL') + endpoint  # Use API_URL from .env
    headers = {
        'x-apisports-key': api_key
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def write_to_bigquery(table_id: str, json_data: dict, fixture_id: int) -> None:
    """
    Unpacks json and sends the data to BigQuery table.
    """
    client = bigquery.Client()
    table = client.get_table(table_id)

    rows_to_insert = [
        {
            "ingestion_timestamp": pendulum.now().to_datetime_string(),
            "id": fixture_id,
            "data": json.dumps(json_data)  # Store the entire response as JSON in the 'data' column
        }
    ]

    errors = client.insert_rows(table, rows_to_insert)
    if errors:
        print(f"BigQuery insert errors: {errors}")  # Log any insertion errors
        raise Exception(f"Failed to insert rows: {errors}")
    print(f'Inserted {len(rows_to_insert)} rows into {table_id}')




def fetch_and_store_statistics(api_key: str, fixture_ids: list) -> None:
    """
    Fetches fixture statistics for the last 50 games and stores them in BigQuery.
    """
    endpoint = "fixtures/statistics"
    table_id = "team-god.football_data.raw_fixture_statistics"

    for i, fixture_id in enumerate(fixture_ids):
        if i > 0 and i % 10 == 0:
            print("Pausing for 60 seconds to avoid exceeding rate limit...")
            time.sleep(60)  # Pause for 60 seconds after every 10 requests

        params = {
            "fixture": fixture_id
        }

        data = fetch_data(endpoint, api_key, params)

        if data['response']:
            # Store statistics data into BigQuery for each fixture
            write_to_bigquery(table_id, data['response'], fixture_id)
        

# --- Fetch Fixture Details and Write to BigQuery ---
def fetch_and_store_fixtures(api_key: str, team_id: int, venue_id: int, limit: int) -> list:
    """
    Fetches fixture details for the last 50 games and stores them in BigQuery.
    Only fetches fixtures where the venue ID matches the specified venue.
    """
    endpoint = "fixtures"
    table_id = "team-god.football_data.raw_fixture_details"

    params = {
        # "team": team_id,
        "last": limit,
        "venue": venue_id
    }

    data = fetch_data(endpoint, api_key, params)

    fixture_ids = []
    
    for fixture in data['response']:
        fixture_id = fixture['fixture']['id']
        fixture_ids.append(fixture_id)
        # Store fixture data into BigQuery
        write_to_bigquery(table_id, fixture, fixture_id)

    return fixture_ids

# --- Main Function ---
@app.get("/")
def main():
    # Get API Key and other details from environment
    api_key = os.getenv('API_KEY')
    team_id = 363  # The team ID
    venue_id = 1506  # Tele2 Arena
    limit = 95  # Fetch the last 95 games

    if not api_key:
        raise HTTPException(status_code=500, detail="API_KEY not set")

    try:
        # Fetch and store fixture details, and get list of fixture IDs for the last 50 games at the venue
        # fixture_ids = fetch_and_store_fixtures(api_key=api_key, team_id=team_id, venue_id=venue_id, limit=limit)
        fixture_ids = fetch_and_store_fixtures(api_key=api_key, team_id=team_id, venue=venue_id, limit=limit)


        # Fetch and store fixture statistics for the filtered games
        fetch_and_store_statistics(api_key=api_key, fixture_ids=fixture_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {e}")
    
    return {"status_code": 200, "message": "Data fetched and stored successfully"}


# docker build -t gcr.io/team-god/api-football-raw .
# docker push gcr.io/team-god/api-football-raw
# gcloud auth configure-docker
# gcloud run deploy api-football-raw-service --image gcr.io/team-god/api-football-raw --platform managed --region europe-north1 --concurrency 2 --max-instances 2
# gcloud run services delete SERVICE_NAME --region europe-north1