from dotenv import load_dotenv
import os
import requests


load_dotenv()
api_key = os.environ.get("API_KEY")

params = {"access_key": api_key}

api_result = requests.get(
    "http://api.aviationstack.com/v1/flights?access_key=54976084ba68b58770c67fbd423614a0"
)

api_response = api_result.json()

current_flights = []
for item in api_response["data"]:
    if item["airline"]["name"] == "KLM":
        current_flights.append(item)

print(current_flights)
