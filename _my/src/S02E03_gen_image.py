import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"
task_name = "robotid"

def get_robot_description():
    url = f"https://c3ntrala.ag3nts.org/data/{my_key}/robotid.json"
    response = requests.get(url)
    return response.json()

def generate_image_prompt(description):
    prompt = f"""Jesteś ekspertem od tworzenia promptów do modeli generujących obrazy.
    Twoim zadaniem jest przygotowanie opisu obrazu, który będzie wykorzystany do wygenerowania obrazu robota na podstawie zeznania świadka.
    Opis powinien być zrozumiały dla modelu DALL-E.
    Opis powinien zawierać szczegółowe informacje o robotach, pracujących w fabryce.
    Zeznanie świadka: {description}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "text"}
    )
    return response.choices[0].message.content

def generate_image(prompt):
    response = client.images.generate(
        prompt=prompt,
        model="dall-e-3",
        size="1024x1024"
    )
    return response.data[0].url

def make_json(data):
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

if __name__ == "__main__":
    json_data = get_robot_description()
    print(json_data["description"])
    prompt = generate_image_prompt(json_data["description"])
    print(prompt)
    image_url = generate_image(prompt)
    print(image_url)
    json_data = make_json(image_url)
    response = send_json(json_data)
    print(response)
