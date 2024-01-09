from dotenv import load_dotenv
import os
import requests
from pprint import pprint


load_dotenv()
api_key = os.environ.get("API_KEY")

params = {"access_key": api_key}

api_result = requests.get("http://api.aviationstack.com/v1/airlines", params)

api_response = api_result.json()

air_france_general_data = api_response["data"][17]

desired_dict = next(
    (item for item in api_response["data"] if item.get("airline_name") == "Air France"),
    None,
)

print(desired_dict)
