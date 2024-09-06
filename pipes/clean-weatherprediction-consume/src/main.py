from google.cloud import bigquery
import joblib
from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime
import pendulum

app = FastAPI()
model = joblib.load("weather_forecasting_model_stockholm_xgb.pkl")

expected_columns = [
    "hour", 
    "month", 
    "temp", 
    "humidity", 
    "pressure", 
    "temp_lag_1", 
    "temp_lag_3"
]

@app.get("/bigquery_test")
def read() -> list:
    """Fetch weather-data from BigQuery"""
    try:
        with bigquery.Client() as client:
            query = """
            SELECT hour, month, temp, humidity, pressure, temp_lag_1, temp_lag_3, temp_time
            FROM `team-god.weather_data.clean_weatherapp` 
            LIMIT 24
            """
            df = client.query(query).to_dataframe()
            return df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")

        
@app.get("/predict")
def predict() -> list:
    """Making a prediction based on the input from BigQuery"""

    try:
        input_data = read()
        
        df = pd.DataFrame(input_data)
        df = df[expected_columns]
        
        predictions = model.predict(df)
        prediction_results = predictions.tolist()

        combined_results = [
            {"datetime": input_row["temp_time"], "prediction": prediction}
            for input_row, prediction in zip(input_data, prediction_results)
        ]

        return combined_results
    
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing expected column: {str(e)}")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

def write(json_data: dict) -> None:
    """
    Unpacks json and sends the data to BigQuery table.
    """
    client = bigquery.Client()
    table_id = "team-god.weather_data.raw_predictions_weatherapp"
    table = client.get_table(table_id)

    rows_to_insert = [
        {
            "datetime": datetime.strptime(hour['datetime'], "%Y-%m-%d %H:%M").isoformat(),
            "prediction": hour['prediction'],
            "timestamp": pendulum.now().to_datetime_string()
        }
        for hour in json_data
    ]

    errors = client.insert_rows(table, rows_to_insert)
    if errors:
        raise Exception(f"Failed to insert rows: {errors}")
    print(f'Inserted {len(rows_to_insert)} rows')


@app.get("/")
def main():
    data = predict()

    try:
        data=write(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert to BigQuery failed: {e}")
    
    return {"status_code": 200}
