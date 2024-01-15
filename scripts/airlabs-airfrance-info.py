from dotenv import load_dotenv
import os
import requests
from pprint import pprint


load_dotenv()
api_key = os.environ.get("AIRLABS_KEY")

params = {"access_key": api_key}

api_result = requests.get(
    "https://airlabs.co/api/v9/airlines?iata_code=AF&api_key=80918319-c19e-4235-aa84-357bfc626cd3"
)

api_response = api_result.json()

print(api_response)
