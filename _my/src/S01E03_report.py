import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"

def get_data():
    url = f"https://c3ntrala.ag3nts.org/data/{my_key}/json.txt"
    response = requests.get(url)
    return response.json()

def calculate_answer(question):
    # split question by space
    question = question.split(" ")
    # if question contains "plus" or "+" then add the numbers
    if "plus" in question or "+" in question:
        return int(question[0]) + int(question[2])
    print("warning: unknown question")

def get_answer(question):
    prompt = f"""You are a helpful assistant
    You are given a question and you need to answer it.
    Answer as short as possible.
    <examples>
    Question: What is the capital of Poland?
    Answer: Warsaw
    Question: What is the capital of France?
    Answer: Paris
    Question: What is the capital of Germany?
    Answer: Berlin
    </examples>
    Question: {question}
    Answer:
    """
    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )
    return response.output_text

def make_json(data):
    json_data = {
        "task": "JSON",
        "apikey": my_key,
        "answer": data
    }
    return json_data

def send_json(json_data):
    url = "https://c3ntrala.ag3nts.org/report"
    response = requests.post(url, json=json_data)
    return response.json()

if __name__ == "__main__":
    data = get_data()
    response = {"apikey": my_key, "description": data.get("description"), "copyright": data.get("copyright"), "test-data": []}
    for item in data.get("test-data"):
        answer = calculate_answer(item.get("question"))
        #print(item.get("question") + " " + str(item.get("answer")) + " -> " + str(answer))
        if not item.get("test") is None:
            test_answer = get_answer(item.get('test').get('q'))
            print(f"{item.get('test').get('q')} {item.get('test').get('a')} -> {test_answer}")
            response.get("test-data").append({"question": item.get("question"), "answer": answer, "test": {"q": item.get('test').get('q'), "a": test_answer}})
        else:
            response.get("test-data").append({"question": item.get("question"), "answer": answer})
    json_data = make_json(response)
    response = send_json(json_data)
    print(response)
