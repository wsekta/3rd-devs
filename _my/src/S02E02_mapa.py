import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI
from PIL import Image
load_dotenv()
client = OpenAI()

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"


def locate_map(imag_url):
    prompt = """Jesteś ekspertem geograficznym.
    Masz do dyspozycji cztery fragmenty mapy.
    Wszystkie fragmenty są z miasta w Polsce.
    Twoim zadaniem jest określenie miasta, które jest reprezentowane przez mapę.
    Jedna z map jest z innego miasta i należy ją odrzucić.
    W mieście tym znajdują się spichlerze i twierdze.
    W znaczniku <thinking> podaj swoje rozumowanie, wypisz ulice i charakterystyczne obiekty i układ urbanistyczny miasta.
    W znaczniku <answer> podaj nazwę miasta.
    """
    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": imag_url,
                },
            ],
        }],
    )
    print(response.output_text)
    return response.output_text
    

if __name__ == "__main__":
    locate_map("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCT29LSmdVPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--4c8897042c920fe1eb0e51f35cdc8a4a2eda2f38/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNIYVFMUUIya0MwQWM2Q25OaGRtVnlld1k2Q25OMGNtbHdWQT09IiwiZXhwIjpudWxsLCJwdXIiOiJ2YXJpYXRpb24ifX0=--ced9b89e636fbe4e9d139673c30ec65b0d14eccd/Mapy_A4_2stronny_spad5mm-1.png")