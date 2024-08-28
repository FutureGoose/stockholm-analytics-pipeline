import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import psycopg2
import pendulum

app = FastAPI()
load_dotenv()


def fetch_weather_data(api_url: str, longitude: str, latitude: str, parameter: str, from_date: str, to_date: str) -> dict:
    """
    Fetches weather data from API.
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    
    print(f"Fetching data from URL: {api_url}")
    try:
        response = requests.get(f"{api_url}/{longitude}/lat/{latitude}/parameter/{parameter}/data.json", params=params)
        response.raise_for_status()
        print("Fetched data from API")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

api_url = os.getenv('API_URL')
print(f"API URL: {api_url}")

longitude = 18.0649
latitude = 59.33258
parameter = 118
from_date = "2020-02-01"
to_date = "2020-02-01"

print(fetch_weather_data(api_url, longitude, latitude, parameter, from_date, to_date))

