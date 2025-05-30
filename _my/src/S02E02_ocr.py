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

def ocr_image(imag_url):
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
                    "image_url": imag_url,
                },
            ],
        }],
    )
    print(response.output_text)
    return response.output_text
    

if __name__ == "__main__":
    ocr_image("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCS0prd2dNPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--77be9d2df7098a5f996cd067429ca88de1a2a33e/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJY0c1bkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNITUdrQ09BUTZDbk5oZG1WeWV3WTZDbk4wY21sd1ZBPT0iLCJleHAiOm51bGwsInB1ciI6InZhcmlhdGlvbiJ9fQ==--cfda350175ba87e768b4e96e935a8171fc679bec/s02e02_tmp.png")
    ocr_image("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCQ2dDSmdVPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--fefb459c3b32582ee9a2750b7b59a565d8d19d0a/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNIYVFMUUIya0MwQWM2Q25OaGRtVnlld1k2Q25OMGNtbHdWQT09IiwiZXhwIjpudWxsLCJwdXIiOiJ2YXJpYXRpb24ifX0=--ced9b89e636fbe4e9d139673c30ec65b0d14eccd/2_Zagubiona_karta_A4_CMYK_jedostronna_druk_040425-1.png")