import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"
task_name = "mp3"

def handle_audios(audio_dir):
    for file in os.listdir(audio_dir):
        if file.endswith(".m4a"):
            print(f"Przesłuchanie {file}")
            audio_file = open(os.path.join(audio_dir, file), "rb")
            transcript = transcribe(audio_file)
            print(f"Przesłuchanie {file}: {transcript}")
            with open(os.path.join(audio_dir, file.replace(".m4a", ".txt")), "w") as f:
                f.write(transcript)

def transcribe(audio_url):
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_url
    )
    return response.text

def handle_transcripts(transcript_dir):
    combined_transcript = ""
    for file in os.listdir(transcript_dir):
        if file.endswith(".txt"):
            combined_transcript += f"Transkrypcja {file[:-4]}:\n"
            with open(os.path.join(transcript_dir, file), "r") as f:
                transcript = f.read()
            combined_transcript += transcript + "\n\n"
    print(combined_transcript)
    answer = check_if_talks_about_institute(combined_transcript)
    print(answer)
    return answer

def check_if_talks_about_institute(transcript):
    prompt = f"""Jesteś detektywem.
    Twoim zadaniem jest ustalenie ulicy na której znajduje się instytut w którym pracuje Andrzej Maj.
    Zapisz tok myślenia w klamrach <thinking>...</thinking> gdzie przeanalizujesz transkrypcję krok po kroku.
    Zwróć wynik w klamrach <answer>...</answer> w formacie "ul. [ulica]"
    Użyj całej dostępnej wiedzy do ustalenia ulicy.
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript}
        ]
    )
    return response.choices[0].message.content

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
    handle_audios(os.path.join(os.path.dirname(__file__), "data", "przesluchania"))
    answer = handle_transcripts(os.path.join(os.path.dirname(__file__), "data", "przesluchania"))
    answer = answer.split("<answer>")[1].split("</answer>")[0]
    answer = "ul. prof. Stanisława Łojasiewicza"
    print(answer)
    json_data = make_json(answer)
    response = send_json(json_data)
    print(response)
