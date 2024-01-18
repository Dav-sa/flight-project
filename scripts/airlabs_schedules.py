from dotenv import load_dotenv
import os
import requests
from pprint import pprint
import json

load_dotenv()
api_key = os.environ.get("AIRLABS_KEY")

params = {"api_key": api_key}

api_result = requests.get("https://airlabs.co/api/v9/schedules", params)

print(api_result.content)

"""with open("schedules.json", "w") as file:
    json.dump(api_response, file, indent=4)

pprint(api_response)
"""
