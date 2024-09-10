from pytrends.request import TrendReq
import pandas as pd
from google.cloud import bigquery
from fastapi import FastAPI, HTTPException
from typing import List
import pendulum
from pytz import timezone
import time
from requests.exceptions import HTTPError


swedish_tz = timezone('Europe/Stockholm')

# Initialize pytrends request
pytrends = TrendReq(hl='sv', tz=int(pendulum.now(swedish_tz).offset / 60))

# Define keywords
kw_list_1 = ["fläkt", "jacka", "solglasögon", "solkräm", "badkläder"]
kw_list_2 = ["snaps", "glass", "grill", "jordgubbar", "sill"]
kw_list_3 = ["varm choklad", "glögg", "earl grey", "chai", "mojito"]
kw_list_4 = ["jacka", "paraply", "storm", "mössa", "päls"]

kw_lists = [kw_list_1, kw_list_2, kw_list_3, kw_list_4]

# Define the project and dataset details for BigQuery
project_id = 'team-god'
dataset_id = 'google_trends'
table_id_prefix = 'searchwords_new'

app = FastAPI()


def fetch_trends_data(kw_list: List[str]) -> pd.DataFrame:
    """
    Fetch Google Trends data for the given list of keywords.
    """
    # Payload with settings "all categories", "past week", "Stockholm" and "web searches"
    pytrends.build_payload(kw_list, cat=0, timeframe='now 3-m', geo='SE-AB', gprop='')
    data = pytrends.interest_over_time()
    
    # Add ingestion timestamp as a datetime object
    data['ingestion_timestamp'] = pd.to_datetime(pendulum.now().to_datetime_string())

    # Normalize column names (handle Swedish characters)
    data.columns = [col.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(' ', '_') for col in data.columns]
    
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


@app.get("/")
def main():
    """
    HTTP endpoint to fetch trends data and send it to BigQuery.
    """
    try:
        for idx, kw_list in enumerate(kw_lists):
            trends_data = fetch_trends_data(kw_list)
            send_to_bigquery(trends_data, f"{idx+1}")
            
            # Add 60 seconds of sleep between each request to avoid rate limits
            time.sleep(60)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
            
    return {"status_code": 200}
    