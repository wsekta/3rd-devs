import requests
from dotenv import load_dotenv
import os

load_dotenv()

my_key = os.getenv("MY_KEY")

def make_json(task_name, data):
    json_data = {
        "task": task_name,
        "apikey": my_key,
        "answer": data
    }
    return json_data

def send_json(json_data):
    url = "https://c3ntrala.ag3nts.org/report"
    response = requests.post(url, json=json_data)
    return response.json()