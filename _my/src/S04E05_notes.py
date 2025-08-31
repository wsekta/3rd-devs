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

import pymupdf
import pdf2image


load_dotenv()
client = OpenAI()

my_key = os.getenv("MY_KEY")
task_name = "notes"

poppler_path = r"C:\Users\Wojtek\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin"

def get_questions():
    """get questions from website"""
    url = f"https://c3ntrala.ag3nts.org/data/{my_key}/notes.json"
    response = requests.get(url)
    data = response.json()
    return data

def get_notes():
    """get notes (pdf file) from website and save them to local directory"""
    url = f"https://c3ntrala.ag3nts.org/dane/notatnik-rafala.pdf"
    response = requests.get(url)
    with open("_my/src/data/notatnik-rafala.pdf", "wb") as f:
        f.write(response.content)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def ocr_image(image_path):
    prompt = """You act like a OCR. You are given an image and you need to extract the text from the image.
    You need to return only the text from the image.
    You need to return the text in Polish.
    If there is mentioned city it is probably Lubawa koło Grudziądza.
    """
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{encode_image(image_path)}",
                },
            ],
        }],
    )
    return response.output_text

def get_last_page():
    """last page is image, get it and read it with llm"""
    images = pdf2image.convert_from_path("_my/src/data/notatnik-rafala.pdf", poppler_path=poppler_path, first_page=19)
    image = images[0]
    image.save("_my/src/data/notatnik-rafala-last-page.png")
    text = ocr_image("_my/src/data/notatnik-rafala-last-page.png")
    print(f"Text from last page: {text}")
    return text

def get_note_text():
    """get text from note"""
    doc = pymupdf.open("_my/src/data/notatnik-rafala.pdf")
    text = ""
    for no, page in enumerate(doc):
        if no == 18:
            break
        page_text = f"Strona {no+1}:\n{page.get_text()}"
        text += page_text
    text_from_last_page = f"Strona 19:\n{get_last_page()}"
    text += text_from_last_page
    print(text)
    return text

def get_answer(question, note_text, context):
    """get answer to question from note tex using llm"""
    print(f"Getting answer to question: {question}")
    print(f"Context: {context}")
    system_prompt = f"""
Jesteś ekspertem w czytaniu notatników Rafała.
<prompt_objectives>
W zadaniu masz odpowiedzieć na pytania na podstawie notatnika Rafała.
</prompt_objectives>
<prompt_instructions>
- Odpowiedz na pytanie z sekcji <question> na podstawie notatnika Rafała.
- Odpowiedź musi być zgodna z notatnikiem Rafała.
- Odpowiedź musi być zwięzła i zrozumiała.
- Traktuj notatnik Rafała jak zapis osoby chorej na umyśle.
- Odpowiedź na pewno znajduje się w notatniku Rafała, choć może nie być podana wprost.
- Zapisz swoje przemyślenia w sekcji <thinking>.
- Odpowiedź zapisz w sekcji <answer>.
- Wykorzystaj kontekst z sekcji <context> jeśli jest podany.
- W sekcji <wrong_answer> znajduje się przykładowe odpowiedzi, które są błędne - NIE UŻYWAJ ICH.
</prompt_instructions>
<input_data>
Notatnik Rafała:
{note_text}
</input_data>
"""
    user_prompt = f"""
<question>
{question}
</question>
<context>
{context}
</context>
"""
    response = client.responses.create(
        model="gpt-5",
        input=[{
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }],
    )
    print(response.output_text)
    answer = response.output_text.split("<answer>")[1].split("</answer>")[0]
    return answer

def get_answers(questions: dict, note_text: str):
    """get answers to questions from note text"""
    answers = {
    }
    context = {
        "01": """
Uwzględnij wszystkie fakty podane w tekście, w szczególności odwołania do wydarzeń.
Data powstania GPT-2: 2019-02-14
<wrong_answer>
<thinking>
Nie mogę ujawniać szczegółowego łańcucha rozumowania. W skrócie: w notatniku Rafał jednoznacznie odwołuje się do 2024 roku (m.in. wpis „11 listopada 2024”), co wskazuje, że to do tego roku się przeniósł.
</thinking>
<answer>
2024
</answer>
<thinking>
Na stronie 1 Rafał pisze, że jest w „20… roku” (bez podania dokładnych cyfr). Konkretną kotwicę czasową podaje dopiero na stronie 18: „11 listopada 2024” („To już jutro”), co wskazuje, że znajduje się w roku 2024 po swoim skoku. Pozostałe wzmianki (o GPT-2/3) nie podają wprost roku przybycia, ale 2024 jest jednoznacznie wskazane jako bieżący rok jego misji po przeniesieniu.
</thinking>
<answer>
2024
</answer>
<thinking>
W notatniku Rafał pisze, że „jest w 20... roku” i zaraz potem wspomina plan Adama: zacząć prace nad LLM tak, by najpierw powstało GPT-2, a potem GPT-3. Następnie notuje, że „No i powstało GPT-2. Słyszałem w wiadomościach…”, co historycznie odpowiada 2019. Skoro ma przed sobą „dwa lata intensywnej nauki” i te dwa lata mają doprowadzić go w okolice czasu GPT-3 (2020), najbardziej spójne jest, że przeniósł się do 2018 roku — rok przed GPT-2 i dwa lata przed GPT-3.
</thinking>
<answer>
2018
</answer>
</wrong_answer>
""",
        "04": """
Rafał odwołuje się względnie do tej daty i nie wymienia jej dosłownie w tekście.
To już jutro - następny dzień po podanej dacie. Np to już jutro w kontekście daty 2013-07-04 to 2013-07-05.
<wrong_answer>
<thinking>
Na Stronie 18 Rafał pisze „To już jutro.” i podaje datę „11 listopada 2024”, co wskazuje dzień spotkania.
</thinking>
<answer>
2024-11-11
</answer>
</wrong_answer>
"""
    }
    for question_no, question in questions.items():
        print(f"Getting answer to question: {question}")
        if question_no in answers:
            continue
        context_for_question = context[question_no] if question_no in context else ""
        answer = get_answer(questions[question_no], note_text, context_for_question)
        answers[question_no] = answer
        print(f"Answer to question {question_no}:{question}\n{answer}")
    return answers


if __name__ == "__main__":
    questions = get_questions()
    print(f"Questions to answer: {questions}")
    # get_notes()
    note_text = get_note_text()
    answers = get_answers(questions, note_text)
    json_data = make_json(task_name, answers)
    response = send_json(json_data)
    print(f"Response: {response}")
