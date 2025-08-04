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

load_dotenv()
client = OpenAI()

my_key = os.getenv("MY_KEY")
task_name = "loop"

people_set = set()
people_queue = []
places_set = set()
places_queue = []
unknown_set = set()

def add_person(person):
    if person not in people_set:
        print(f"adding person {person}")
        people_set.add(person)
        people_queue.append(person)

def add_place(place):
    if place not in places_set:
        print(f"adding place {place}")
        places_set.add(place)
        places_queue.append(place)

def get_next_person():
    if len(people_queue) > 0:
        return people_queue.pop(0)
    return None

def get_next_place():
    if len(places_queue) > 0:
        return places_queue.pop(0)

def parse_llm_output(llm_output):
    """ 
    llm output is string with <persons> and <places> tags
    example:
    <persons>
    John Doe
    Jack Smith
    </persons>
    <places>
    New York
    Los Angeles
    </places>
    function add them to global sets
    """
    #find all <persons> and <places> tags
    persons_match = re.search(r"<persons>\s*(.*?)\s*</persons>", llm_output, re.DOTALL)
    places_match = re.search(r"<places>\s*(.*?)\s*</places>", llm_output, re.DOTALL)
    
    if persons_match:
        persons = persons_match.group(1).strip()
        if persons:
            for person in persons.split("\n"):
                person = person.strip()
                if person:
                    add_person(person)

    
    if places_match:
        places = places_match.group(1).strip()
        if places:
            for place in places.split("\n"):
                place = place.strip()
                if place:
                    add_place(place)

def get_people_and_places(input_text):
    """
    put text into llm and get <persons> and <places> tags
    """
    system_prompt = f"""
    You are a helpful assistant that extracts people and places from text.
    You need to extract all people and places from the text.
    Text is in polish language.
    You need to return the text tags <persons> and <places> with all people and places, all in uppercase without special  polish characters and without any other text.
    For names return only first name.
    Example:
    input: Kamil Ślimak przeprowadził się do Warszawy z Krakowa. Poznał tam Aleksandra Nawałkę i Rafała Trzaskowskiego.
    output:
    <persons>
    KAMIL
    ALEKSANDER
    RAFAL
    </persons>
    <places>
    KRAKOW
    WARSZAWA
    </places>
    """
    user_prompt = f"""
    input: {input_text}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    answer = response.choices[0].message.content
    return answer

def query_api(api, query):
    url = ""
    if api == "people":
        url = f"https://c3ntrala.ag3nts.org/people"
    elif api == "places":
        url = f"https://c3ntrala.ag3nts.org/places"
    data = { "apikey": my_key, "query": query }
    response = requests.post(url, json=data)
    return response.json()

def is_person_or_place(text):
    """
    function use api to check if text is person or place
    """
    if text in people_set:
        return "person"
    if text in places_set:
        return "place"
    if text in unknown_set:
        return "unknown"

    response = query_api("people", text)
    if response["code"] == 0:
        return "person"
    print(response)
    response = query_api("places", text)
    if response["code"] == 0:
        return "place"
    print(response)
    unknown_set.add(text)
    return "unknown"

def remove_polish_characters(text):
    """
    remove polish characters
    """
    return text.replace("Ą", "A").replace("Ć", "C").replace("Ę", "E").replace("Ł", "L").replace("Ń", "N").replace("Ó", "O").replace("Ś", "S").replace("Ź", "Z").replace("Ż", "Z")

def parse_api_response(response):
    """
    response is in format:
    PLACE1 PERSON1 PERSON2 PLACE2 PERSON3
    function add them to global sets
    """
    #split response by spaces
    items = response.split(" ")
    for item in items:
        is_person = is_person_or_place(item)
        item = remove_polish_characters(item)
        if is_person == "person":
            add_person(item)
        elif is_person == "place":
            add_place(item)

if __name__ == "__main__":
    # read file from _my/src/data/barbara.txt
    text = ""
    with open("_my/src/data/barbara.txt", "r", encoding="utf-8") as file:
        text = file.read()
    llm_output = get_people_and_places(text)
    parse_llm_output(llm_output)

    while len(people_queue) > 0 or len(places_queue) > 0:
        person = get_next_person()
        if person:
            print(f"person: {person}")
            output = query_api("people", person)
            print(output)
            text = output["message"]
        else:
            place = get_next_place()
            if place:
                print(f"place: {place}")
                output = query_api("places", place)
                print(output)
                text = output["message"]
                if "BARBARA" in text:
                    json_data = make_json(task_name, place)
                    print(send_json(json_data))
            else:
                break
        print(text)
        parse_api_response(text)
        # lllm_output = get_people_and_places(text)
        # print(llm_output)
        # parse_llm_output(llm_output)

    # json_data = make_json(task_name, "LUBLIN")
    # print(send_json(json_data))