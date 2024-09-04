from pytrends.request import TrendReq
import pandas as pd
from google.cloud import bigquery
from fastapi import FastAPI, HTTPException
from typing import List
import pendulum

# Initialize pytrends request
pytrends = TrendReq(hl='sv', tz=120)  # tz = Central European Summer Time

# Define keywords
kw_list_1 = ["fläkt", "jacka", "paraply", "solkräm", "badplats"]
kw_list_2 = ["choklad", "glass", "grill", "jordgubbar", "potatis"]
kw_list_3 = ["varm choklad", "glögg", "earl grey", "chai", "ylle"]

kw_lists = [kw_list_1, kw_list_2, kw_list_3]

# Define the project and dataset details for BigQuery
project_id = 'team-god'
dataset_id = 'google_trends'
table_id_prefix = 'raw_searchwords'

app = FastAPI()

def fetch_trends_data(kw_list: List[str]) -> pd.DataFrame:
    """
    Fetch Google Trends data for the given list of keywords.
    """
    # Payload with settings "all categories", "past 3 months", "Stockholm" and "web searches"
    pytrends.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='SE-AB', gprop='')
    data = pytrends.interest_over_time()
    
    # Add ingestion timestamp as a datetime object
    data['ingestion_timestamp'] = pd.to_datetime(pendulum.now().to_datetime_string())

    # Rename columns to replace spaces with underscores
    data.columns = [col.replace(' ', '_') for col in data.columns]
    
    return data

def send_to_bigquery(data: pd.DataFrame, table_suffix: str) -> None:
    """
    Send the fetched trends data to a BigQuery table.
    """
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset_id}.{table_id_prefix}_{table_suffix}"
    job = client.load_table_from_dataframe(data, table_id)
    job.result()
    print(f"Data successfully loaded to {table_id}")

@app.get("/update_trends")
def update_trends():
    """
    HTTP endpoint to fetch trends data and send it to BigQuery.
    """
    try:
        for idx, kw_list in enumerate(kw_lists):
            trends_data = fetch_trends_data(kw_list)
            send_to_bigquery(trends_data, f"{idx+1}")
        return {"status": "Data processing completed"}, 200
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# docker build -t gcr.io/team-god/pytrends-api-search-clean .
# docker push gcr.io/team-god/pytrends-api-search-clean
# gcloud auth configure-docker
# gcloud run deploy pytrends-api-search-clean-service --image gcr.io/team-god/pytrends-api-search-clean --platform managed --region europe-north1 --concurrency 2 --max-instances 2 --allow-unauthenticated
# gcloud run services delete SERVICE_NAME --region europe-north1

# gcloud run deploy search-trends-api-raw-service  --image gcr.io/team-god/pytrends-api-search-clean --platform managed --region europe-north1 --concurrency 2 --max-instances 2 --allow-unauthenticated
