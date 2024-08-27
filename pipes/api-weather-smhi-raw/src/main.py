import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import psycopg2
import pendulum

app = FastAPI()
load_dotenv()


# Define the base URL and endpoint
base_url = "https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point"

# Define the coordinates, parameters, and date range
longitude = 18.0649
latitude = 59.33258
parameter = 118
from_date = "2020-02-01"
to_date = "2020-02-01"

# Construct the full URL with query parameters
url = f"{base_url}/lon/{longitude}/lat/{latitude}/parameter/{parameter}/data.json"
params = {
    "from": from_date,
    "to": to_date
}

# Send the GET request
response = requests.get(url, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print("Data received:")
    print(data)
else:
    # Handle errors
    print(f"Error: {response.status_code}")
    print(response.text)
