import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_data():
    # URL to fetch data from
    url = "https://xyz.ag3nts.org/"
    
    try:
        # Make GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the text content and split it into lines
        # data = response.text.strip().split('\n')
        
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
def get_human_question(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    # <p id="human-question">
    question = soup.find('p', id="human-question")
    return question.text.strip()

def get_answer(question):
    prompt = f"""You are a helpful assistant with knowledge of history. 
    You are given a question about dates of important events in history.
    You need to answer with the date in format YYYY - year only.
    <examples>
    Question: When was the Battle of Grunwald?
    Answer: 1410
    Question: When did Roman Empire fall?
    Answer: 476
    </examples>
    Question: {question}
    Answer:
    """
    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )
    return response.output_text
    
def send_answer(answer):
    url = "https://xyz.ag3nts.org"
    # username=tester&password=574e112a&answer=ODPOWIEDZ_Z_LLM
    response = requests.post(url, data={"username": "tester", "password": "574e112a", "answer": answer})
    return response.text

if __name__ == "__main__":
    # Get and print the data
    html_text = get_data()
    question = get_human_question(html_text)
    print("Pytanie:", question)
    answer = get_answer(question)
    print("Odpowiedź:", answer)

    response = send_answer(answer)
    print("Status:", response)
