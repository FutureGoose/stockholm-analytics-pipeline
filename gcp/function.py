import datetime
import functions_framework
from flask import jsonify

@functions_framework.http
def get_yesterday_date(request) -> str:
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    formatted_yesterday = yesterday.strftime("%Y-%m-%d")
    return formatted_yesterday