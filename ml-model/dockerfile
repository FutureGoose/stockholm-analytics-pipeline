FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "model_service:app", "--host", "0.0.0.0", "--port", "8080"]