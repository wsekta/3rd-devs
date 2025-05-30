import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64

load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"
task_name = "kategorie"

def files_list_generator(directory):
    for file in sorted(os.listdir(directory)):
        if file.endswith(".txt") or file.endswith(".png") or file.endswith(".mp3"):
            yield file
    return

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

def is_file_in_cache(file):
    return os.path.exists(os.path.join(os.path.dirname(__file__), "tmp", file + ".txt"))

def get_file_from_cache(file):
    with open(os.path.join(os.path.dirname(__file__), "tmp", file + ".txt"), "r") as f:
        return f.read()
    
def save_file_to_cache(file, text):
    with open(os.path.join(os.path.dirname(__file__), "tmp", file + ".txt"), "w") as f:
        f.write(text)

def handle_text(text):
    print(text)

def is_about_people(text):
    prompt = f"""You are a categorizer.
    You need to categorize the text if there are information about capture or seen people.
    You will be given a text in Polish or English.
    You need to return "yes" if there are information about capture or seen people.
    You need to return "no" if there are no information about capture or seen people.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content == "yes"

def is_about_hardware(text):
    prompt = f"""You are a categorizer.
    You need to categorize the text if there are information about fixing or repairing hardware.
    You will be given a text in Polish or English.
    You need to return "yes" if there are information about hardware.
    If there are information about fixing or repairing software, you need to return "no".
    You need to return "no" if there are no information about hardware.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content == "yes"
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
    directory = os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki")
    files = list(files_list_generator(directory))
    print(files, "\n\n")
    people_files = []
    hardware_files = []
    for file in files:
        print(f"{file}: ")

        text = ""
        if file.endswith(".txt"):
            print("type: text")
            with open(os.path.join(directory, file), "r") as f:
                text = f.read()


        if file.endswith(".mp3"):
            print("type: audio")
            if is_file_in_cache(file):
                text = get_file_from_cache(file)
            else:
                text = transcribe(open(os.path.join(directory, file), "rb"))
                save_file_to_cache(file, text)

        if file.endswith(".png"):
            print("type: image")
            if is_file_in_cache(file):
                text = get_file_from_cache(file)
            else:
                text = ocr_image(os.path.join(directory, file))
                save_file_to_cache(file, text)
        
        if is_about_people(text):
            print("category: people")
            people_files.append(file)
        elif is_about_hardware(text):
            print("category: hardware")
            hardware_files.append(file)
        else:
            print("category: unknown")
    
    json_data = make_json({"people": people_files, "hardware": hardware_files})
    print(json_data)
    print(send_json(json_data))


