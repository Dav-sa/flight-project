from dotenv import load_dotenv
import os
import requests
from pprint import pprint
import json

load_dotenv()
api_key = os.environ.get("AIRLABS_KEY")

params = {"api_key": api_key}

api_result = requests.get(
    "https://airlabs.co/api/v9/schedules?airline_icao=AFR&api_key=59c68e10-14f1-45c8-8faa-a38abb8681b6"
)

api_response = api_result.json()["response"]


pprint(api_response)
