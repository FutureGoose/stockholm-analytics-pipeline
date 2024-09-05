import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
import pendulum
from fastapi.responses import JSONResponse

# initialize FastAPI
app = FastAPI()
# load environment variables
load_dotenv()