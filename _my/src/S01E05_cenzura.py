import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI

from library import make_json, send_json

load_dotenv()
client = OpenAI()

task_name = "CENZURA"

def get_data():
    url = f"https://c3ntrala.ag3nts.org/data/{os.getenv('MY_KEY')}/cenzura.txt"
    response = requests.get(url)
    return response.text

def censor(text):
    prompt = f"""You are a censor.
    You are given a text and you need to censor it from personal data.
    You should replace all personal data with "CENZURA".
    As a personal data, you should consider:
    - full name
    - age
    - city
    - address
    - street and house number
    If street and house number are given, you should replace them with only one word "CENZURA".
    <examples>
    Question: Nazywał się Jan Kowalski i mieszkał w Warszawie przy ulicy Kwiatkowskiego 12/34.
    Answer: Nazywał się CENZURA i mieszkał w CENZURA przy ulicy CENZURA.
    Question: Barbara Nowak, 34 lata, mieszka właśnie w tym domu.
    Answer: CENZURA, CENZURA lata, mieszka właśnie w tym domu.
    Question: Miał wtedy 34 lata.
    Answer: Miał wtedy CENZURA lata.
    Question: Mieszkał przy ul. Równej 34 i miał wtedy 27 lat.
    Answer: Mieszkał przy ul. CENZURA i miał wtedy CENZURA lata.
    Question: Widziałem Michała Lewandowskiego. Mieszkał w Warszawie przy ul. Kwiatkowskiego 7.
    Answer: Widziałem CENZURA. Mieszkał w CENZURA przy ul. CENZURA.
    </examples>
    Question: {text}
    Answer:
    """
    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )
    return response.output_text

if __name__ == "__main__":
    data = get_data()
    print(data)
    answer = censor(data)
    print(answer)
    json_data = make_json("CENZURA", answer)
    response = send_json(json_data)
    print(response)
