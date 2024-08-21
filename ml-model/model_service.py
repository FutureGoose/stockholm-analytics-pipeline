from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

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

@app.get("/")
async def read_root():
    return {"message": "Welcome to the ML-Model API"}

@app.post("/predict")
def predict(data: InputData):
    try:
        # Convert input data to DataFrame using model_dump() method
        input_df = pd.DataFrame([data.model_dump()])

        # Perform prediction
        prediction = model.predict(input_df)
        
        # Handle prediction result
        if hasattr(prediction, 'tolist'):
            prediction = prediction.tolist()
        elif isinstance(prediction, (np.float32, np.float64)):
            prediction = float(prediction)

        # Return the prediction
        return {"prediction": prediction[0]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# To run the FastAPI server:
# uvicorn model_service:app --reload
