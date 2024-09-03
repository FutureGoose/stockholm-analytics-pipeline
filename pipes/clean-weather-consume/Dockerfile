FROM google/cloud-sdk:slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-venv && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY src /app/src

COPY gcp-key.json /app/gcp-key.json

# get model from GCP bucket
RUN . venv/bin/activate && \
    gcloud auth activate-service-account --key-file=/app/gcp-key.json && \
    gsutil cp gs://weather-model/weather_forecasting_model_stockholm_xgb.pkl /app/

CMD ["venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]






# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY src /app/src

# COPY weather_forecasting_model_stockholm_xgb.pkl /app/

# EXPOSE 8080

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]