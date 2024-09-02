from pytrends.request import TrendReq
import pandas as pd
from google.cloud import bigquery

# Initialize pytrends request
pytrends = TrendReq(hl='sv', tz=120) # tz = minutes offset from UTC

# Define keywords
kw_list_1 = ["fläkt", "jacka", "paraply", "solkräm", "badplats"]
kw_list_2 = ["choklad", "glass", "grill", "jordgubbar", "potatis"]
kw_list_3 = ["varm choklad", "glögg", "earl grey", "chai", "ylle"]

kw_lists = [kw_list_1, kw_list_2, kw_list_3]

# Define the project and dataset details for BigQuery
project_id = 'team_god'
dataset_id = 'google_trends'
table_id_prefix = 'search_words'

def fetch_trends_data(kw_list):

    # Payload with settings "all categories", "past 3 months", "Stockholm" and "web searches"
    pytrends.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='SE-AB', gprop='')

    # Get the interest over time (daily data)
    data = pytrends.interest_over_time()

    # Check if there is a 'isPartial' column and drop it if necessary
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])
    
    return data


def send_to_bigquery(data, table_suffix):


    # Create a BigQuery client
    client = bigquery.Client(project=project_id)

    # Define the full table ID
    table_id = f"{project_id}.{dataset_id}.{table_id_prefix}_{table_suffix}"

    # Load the data to BigQuery
    job = client.load_table_from_dataframe(data, table_id)

    # Wait for the job to complete
    job.result()

    print(f"Data successfully loaded to {table_id}")

# Iterate through the keyword lists
for idx, kw_list in enumerate(kw_lists):
    # Fetch the data
    trends_data = fetch_trends_data(kw_list)
    # Send the data to BigQuery with a unique table suffix (kw_list_1, kw_list_2, etc.)
    send_to_bigquery(trends_data, f"kw_list_{idx+1}")
