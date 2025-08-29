import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
from library import make_json, send_json
import re
import argparse
from flask import Flask
import ssl
from flask import request, jsonify

load_dotenv()
client = OpenAI()

my_key = os.getenv("MY_KEY")
task_name = "webhook"

# Create Flask app
app = Flask(__name__)

def prepare_response(description):
    # make json
    json_data = {
        "description": description
    }
    return json_data

def get_position(instruction):
    """using llm based on instruction return position"""
    system_prompt = f"""
Jesteś ekspertem od ustalania pozycji drona na podstawie instrukcji na mapie 4x4.
<prompt_objectives>
- zwróć pozycję drona na mapie 4x4 w formacie x,y gdzie x odległość od lewej krawędzi, y odległość od górnej krawędzi
</prompt_objectives>
<prompt_rules>
- x i y są liczbami całkowitymi, w przedziale 0-3
- instrukcja jest w języku polskim
- zwracane x i y są oddzielone przecinkiem
- nie zwracaj żadnych innych informacji niż pozycja x,y
</prompt_rules>
<prompt_examples>
<example>
- instrukcja: poleciałem jedno pole w prawo
- pozycja: 1,0
</example>
<example>
- instrukcja: jedno w dół
- pozycja: 0,1
</example>
<example>
- instrukcja: poleciałem dwa pola w prawo, potem dwa w dół i jedno w lewo
- pozycja: 1,2
</example>
</prompt_examples>
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": instruction}]
    )
    result = response.choices[0].message.content.split(",")
    print(f"LLM position: {result}")
    return int(result[0]), int(result[1])

def map_position_to_description(x, y):
    map_description = [
        ["Start", "Łąka", "Drzewo", "Dom"],
        ["Łąka", "Wiatrak", "Łąka", "Łąka"],
        ["Łąka", "Łąka", "Skały", "Dwa drzewa"],
        ["Góry", "Góry", "Samochód", "Jaskinia"]
    ]
    print(f"Map description({x}, {y}): {map_description[y][x]}")
    return map_description[y][x]

def process_json(json_data):
    print("Received JSON data:")
    if "instruction" not in json_data:
        print("No instruction found")
        return
    instruction = json_data["instruction"]
    print(f"Received instruction: {instruction}")
    x, y = get_position(instruction)
    description = map_position_to_description(x, y)
    return prepare_response(description)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return "Hello World"
    # Get JSON data from request
    json_data = request.get_json()
    if json_data:
        response = process_json(json_data)
        print(f"Response: {response}")
        return jsonify(response), 200
    else:
        print("POST request received but no JSON data found")
    return "POST request received and logged", 200


if __name__ == "__main__":
    # Argument parser for mutually exclusive flags --server and --initialize/--init
    parser = argparse.ArgumentParser(description="Webhook script running server or initialize actions.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--server', action='store_true', help='Run server')
    # Allow both --initialize and --init as valid flags for initialization
    group.add_argument('--initialize', '--init', dest='initialize', action='store_true', help='Initialize actions')
    args = parser.parse_args()

    if args.server:
        print("Running HTTPS server on https://localhost:5000")
        print("Visit https://localhost:5000 to see 'hello world'")
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    elif args.initialize:
        print("Initializing actions")
        json_data = make_json(task_name, "https://azyl-54245.ag3nts.org/")
        print(f"Sending JSON data: {json_data}")
        response = send_json(json_data)
        print(f"Response: {response}")
    else:
        print("No action specified")