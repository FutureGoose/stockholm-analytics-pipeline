from google.cloud import bigquery
import joblib
from fastapi import FastAPI, HTTPException
import pandas as pd


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
def query_bigquery() -> list:
    """Fetch weather-data from BigQuery"""
    try:
        client = bigquery.Client()
        
        query = """
        SELECT hour, month, temp, humidity, pressure, temp_lag_1, temp_lag_3 
        FROM `team-god.weather_data.clean_weatherapp` 
        LIMIT 24
        """
        
        df = client.query(query).to_dataframe()
        return df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")

        
@app.get("/")
def predict() -> list:
    """Making a prediction based of the input from BigQuery"""

    try:
          
        input_data = query_bigquery()
        
        df = pd.DataFrame(input_data)
        df = df[expected_columns]
        
        predictions = model.predict(df)
        prediction_results = predictions.tolist()

        combined_results = [
            {"hour": input_row["hour"], "prediction": prediction}
            for input_row, prediction in zip(input_data, prediction_results)
        ]

        return combined_results
    
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing expected column: {str(e)}")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

