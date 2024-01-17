from dotenv import load_dotenv
import os
import requests
from pprint import pprint


load_dotenv()
api_key = os.environ.get("AIRLABS_KEY")

params = {"icao_code": "AFR", "api_key": api_key}

api_result = requests.get(
    "https://airlabs.co/api/v9/airlines"
)

api_response = api_result.json()

print(api_response)
