import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
from html_to_markdown import convert_to_markdown
import re
from library import make_json, send_json

load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"
task_name = "arxiv"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def ocr_image(image_path):
    prompt = """You act like a OCR. You are given an image and you need to extract the text from the image.
    You need to return only the text from the image.
    You need to return the text in Polish.
    If there is no text in the image, you need to return "no text".
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

def transcribe(audio_file):
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return response.text

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

def get_arxiv_data():
    url = "https://c3ntrala.ag3nts.org/dane/arxiv-draft.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for img in soup.find_all("img"):
        img["src"] = f"https://c3ntrala.ag3nts.org/dane/{img['src']}"
    for link in soup.find_all("a"):
        if link.get("href", "").endswith(".mp3"):
            link["href"] = f"https://c3ntrala.ag3nts.org/dane/{link['href']}"

    return soup.prettify()

def describe_image(image_url, text_below_image):
    prompt = f"""You are a helpful assistant that describes images.
    You need to describe the image to save all the information from the image.
    Add details about the image like location, time, people, etc.
    If you guessing location, add the country, city, etc. Try to be as specific as possible. If it is hard to guess, it is probably "Kraków".
    You need to return the description in Polish.
    Text below image which can you understand image: {text_below_image}
    """
    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": image_url,
                },
            ],
        }],
    )
    return response.output_text

def replace_images_with_llm_description(md):
    #find all images in the markdown and text below them
    images = re.findall(r"\!\[\]\((.*?)\)", md)
    text_below_images = re.findall(r"\!\[.*?\]\(.*?\)\n*(.*)\n", md)
    for image, text in zip(images, text_below_images):
        # print(image)
        # print(text)
        # print("--------------------------------")
        description = describe_image(image, text)
        #replace the image with the description
        md = md.replace(f"![]({image})", f"opis obrazu: **{description}**")
    return md

def replace_link_to_audio_with_transcription(md):
    #find all links to audio files
    links = re.findall(r"\[.*?\]\((.*\.mp3)\)", md)
    for link in links:
        #download the audio file
        response = requests.get(link)
        with open("_my\\src\\tmp\\audio.mp3", "wb") as f:
            f.write(response.content)
        #transcribe the audio file
        audio_file = open("_my\\src\\tmp\\audio.mp3", "rb")
        transcription = transcribe(audio_file)
        #replace the link with the transcription
        md = md.replace(link, f"transkrypcja audio: **{transcription}**")
        print(link)
    return md

def get_question_to_article():
    url = f"https://c3ntrala.ag3nts.org/data/{my_key}/arxiv.txt"
    response = requests.get(url)
    questions = {}
    for line in response.text.split("\n"):
        split = line.split("=")
        if len(split) == 2:
            questions[split[0]] = split[1]

    return questions

def get_answer_to_question(question, article_md):
    prompt = f"""You are a helpful assistant that answers questions based on the article.
    You need to answer the question in Polish.
    You should respond with short answer.
    Question: {question}
    Article: {article_md}
    """
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
            ],
        }],
    )
    return response.output_text

if __name__ == "__main__":
    data = get_arxiv_data()
    md = convert_to_markdown(data)
    md = replace_images_with_llm_description(md)
    md = replace_link_to_audio_with_transcription(md)
    os.makedirs("tmp", exist_ok=True)
    with open("_my\\src\\tmp\\arxiv.md", "w", encoding="utf-8") as f:
        f.write(md)
    # print(md)
    question = get_question_to_article()
    responses = {}
    for key, value in question.items():
        print(key)
        print(value)
        answer = get_answer_to_question(value, md)
        print(answer)
        responses[key] = answer
        print("--------------------------------")
    json_data = make_json(responses)
    result = send_json(json_data)
    print(result)

