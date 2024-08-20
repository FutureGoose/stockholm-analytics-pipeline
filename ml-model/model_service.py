from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load the pre-trained model
model = joblib.load("weather_forecasting_model_stockholm_xgb.pkl")

# Define the input data schema
class InputData(BaseModel):
    hour: int
    month: int
    temp: float
    humidity: float
    pressure: float
    temp_lag_1: float
    temp_lag_3: float
    # Add all features expected by your model

@app.post("/predict")
def predict(data: InputData):
    # Convert input data to DataFrame (or any format expected by your model)
    input_df = pd.DataFrame([data.dict()])

    # Perform prediction
    try:
        prediction = model.predict(input_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    # Return the prediction
    return {"prediction": prediction[0]}

# To run the FastAPI server:
# uvicorn model_service:app --reload
