FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

# get model from GCP bucket
RUN apt-get update && apt-get install -y curl gnupg && \
    curl https://sdk.cloud.google.com | bash && \
    /bin/bash -c "source /root/.bashrc" && \
    gcloud auth activate-service-account --key-file=/app/gcp-key.json && \
    gsutil cp gs://weather-model/weather_forecasting_model_stockholm_xgb.pkl /app/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]






# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY src /app/src

# COPY weather_forecasting_model_stockholm_xgb.pkl /app/

# EXPOSE 8080

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]