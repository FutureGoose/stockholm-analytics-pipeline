from fastapi import FastAPI, Query
from google.cloud import bigquery
from pydantic import BaseModel
import joblib

app = FastAPI()

# Load the model
model = joblib.load('model.joblib')

@app.get("/predict")
async def predict(
    hour: int,
    month: int,
    temp: float,
    humidity: float,
    pressure: float,
    temp_lag_1: float,
    temp_lag_3: float):

    # Fetch data from BigQuery
    client = bigquery.Client()
    query = f"""
    SELECT * FROM `team-god.weather_data.clean_weatherapp`
    """
    df = client.query(query).to_dataframe()

    # Assuming your model requires similar data format
    features = df[['hour', 'month', 'temp', 'humidity', 'pressure', 'temp_lag_1',
    'temp_lag_3']].iloc[0]

    # Make prediction
    prediction = model.predict([features])[0]

    return {"max_temperature_prediction": prediction}


# To run the FastAPI server:
# uvicorn model_service:app --reload
