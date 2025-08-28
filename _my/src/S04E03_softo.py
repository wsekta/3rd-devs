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
from html_to_markdown import convert_to_markdown

load_dotenv()
client = OpenAI()

my_key = os.getenv("MY_KEY")
task_name = "softo"

def get_questions():
    """get questions to answer base on softo website"""
    url = f"https://c3ntrala.ag3nts.org/data/{my_key}/softo.json"
    response = requests.get(url)
    data = response.json()
    return data

def get_page_as_markdown(url):
    """get html page from url"""
    response = requests.get(url)
    html_content = response.text
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove all elements with class "hidden"
    hidden_elements = soup.find_all(class_="hidden")
    for element in hidden_elements:
        element.decompose()
    
    # cleaned HTML
    cleaned_html = str(soup)

    # convert to markdown
    markdown = convert_to_markdown(cleaned_html)

    return markdown

def answer_question_base_on_page(question, page):
    """using llm answer question based on page, if answer is not present on page, return `NOT_FOUND`"""
    prompt = f"""
Jesteś specjalistą w zakresie odpowiedzi na pytania dotyczące strony internetowej.
Twoim zadaniem jest znaleźć odpowiedź na pytanie w podanej stronie internetowej.
Jeśli nie znasz odpowiedzi, zwróć NOT_FOUND i nic więcej.
Pytanie: {question}
Strona: {page}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    print(f"LLM searching for answer in page response: {response.choices[0].message.content}")
    return response.choices[0].message.content

def find_next_url(question, page, previous_urls):
    """using llm find next url worth checking to receive answer base on website"""
    #find all links in page in format [text](link)
    links = re.findall(r'\[.*\]\((\S*).*?\)', page)
    available_links = ""
    for link in links:
        available_links += f"{link}\n"
    checked_links = ""
    for link in previous_urls:
        link = link.replace("https://softo.ag3nts.org", "")
        checked_links += f"{link}\n"
    prompt = f"""
Jesteś specjalistą w zakresie znajdywania linków najlepiej dopasowanych do pytani.
Na podanej stronie nie znajduje się odpowiedź na pytanie. 
Podana strona jest w formacie markdown, więc linki są w postaci [text](link).
Spośród linków na stronie, dobierz link do strony gdzie może znajdować się odpowiedź na pytanie.
Link zwróć w postaci /<link>, bez domeny oraz żadnych dodatkowych informacji.
Wybieraj linki z dostępnych linków, które nie były wcześniej sprawdzane.
Jeśli nie ma dostępnych linków, zwróć `NOT_FOUND` i nic więcej.
Pytanie: {question}
Strona: {page}
Dostępne linki (wybierz jeden z tych linków):
{available_links}
Sprawdzone linki (tych linków nie podawaj):
{checked_links}
"""
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"LLM searching for next url response: {response.choices[0].message.content}")
    if response.choices[0].message.content[0] != "/":
        return ""
    domain = "https://softo.ag3nts.org"
    next_url = domain + response.choices[0].message.content
    return next_url


def answer_question(question, url = "https://softo.ag3nts.org/", previous_urls = []):
    """answer question based on url"""
    print(f"Question {question[0]}: checking page {url}")
    page = get_page_as_markdown(url)
    answer = answer_question_base_on_page(question[1], page)
    if answer == "NOT_FOUND":
        print(f"Question {question[0]}: answer not found in page {url}")
        next_url = find_next_url(question[1], page, previous_urls)
        if next_url == "" or next_url == "NOT_FOUND":
            return "Answer not found"
        return answer_question(question, next_url, previous_urls + [url])
    else:
        print(f"Question {question[0]}: answer found in page {url} - {answer}")
        return answer

if __name__ == "__main__":
    # questions = get_questions()
    # answers = dict()
    # for question in questions.items():
    #     print(question)
    #     answers[question[0]] = answer_question(question)
    #     print("--------------------------------")
    # print(answers)
    # print(send_json(make_json(task_name, answers)))
    page = get_page_as_markdown("https://softo.ag3nts.org/portfolio")
    links = re.findall(r'\[.*\]\((\S*).*?\)', page)
    for link in links:
        print(link)