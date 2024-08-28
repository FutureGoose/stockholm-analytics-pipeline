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
    
    # Correct URL structure with lon/longitude and lat/latitude
    full_url = f"{api_url}/lon/{longitude}/lat/{latitude}/parameter/{parameter}/data.json"
    print(f"Fetching data from URL: {full_url}")
    
    try:
        response = requests.get(full_url, params=params)
        response.raise_for_status()
        print("Fetched data from API")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

# # Fetch the API URL from environment variables (or define it here)
# api_url = os.getenv('API_URL') or "https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point"
# print(f"API URL: {api_url}")

# # Define longitude, latitude, parameter, and date range
# longitude = 18.0649
# latitude = 59.33258
# parameter = 118
# from_date = "2020-02-01"
# to_date = "2020-02-02"

# # Fetch the weather data
# print(fetch_weather_data(api_url, longitude, latitude, parameter, from_date, to_date))
