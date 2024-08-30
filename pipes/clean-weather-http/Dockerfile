FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src /app/src

# Copy the model file into the container
COPY weather_forecasting_model_stockholm_xgb.pkl /app/

# Expose port 8080
EXPOSE 8080

# Run Uvicorn with the correct module path
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

