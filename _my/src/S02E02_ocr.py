import requests
from bs4 import BeautifulSoup
#dotenv
from dotenv import load_dotenv
import os
from openai import OpenAI
from PIL import Image
load_dotenv()
client = OpenAI()

from docling.document_converter import DocumentConverter
import json
import time
from pathlib import Path
from docling_core.types.doc import DocItemLabel, ImageRefMode
from docling_core.types.doc.document import DEFAULT_EXPORT_LABELS
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
    smoldocling_vlm_mlx_conversion_options,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline


from doctr.models import ocr_predictor
from doctr.io import DocumentFile

my_key = "da6205a3-9e11-43b8-abae-180bd76be80f"

def ocr_image(imag_url):
    prompt = """You act like a OCR. You are given an image and you need to extract the text from the image.
    You need to return only the text from the image.
    You need to return the text in Polish.
    If there is no text in the image, you need to return "no text".
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
    
def ocr_with_docling(imag_url):
    ## Use experimental VlmPipeline
    pipeline_options = VlmPipelineOptions()
    # If force_backend_text = True, text from backend will be used instead of generated text
    pipeline_options.force_backend_text = False
    # pipeline_options.accelerator_options.device = AcceleratorDevice.CUDA
    pipeline_options.accelerator_options.cuda_use_flash_attention2 = True
    ## Set up pipeline for PDF or image inputs
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options,
            ),
            InputFormat.IMAGE: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options,
            ),
        }
    )
    result = converter.convert(imag_url)
    return result.document.export_to_markdown()

def ocr_with_doctr(imag_url):
    model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    doc = DocumentFile.from_images(imag_url)
    result = model(doc)
    return result

if __name__ == "__main__":
#    text = ocr_with_doctr("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCS0prd2dNPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--77be9d2df7098a5f996cd067429ca88de1a2a33e/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJY0c1bkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNITUdrQ09BUTZDbk5oZG1WeWV3WTZDbk4wY21sd1ZBPT0iLCJleHAiOm51bGwsInB1ciI6InZhcmlhdGlvbiJ9fQ==--cfda350175ba87e768b4e96e935a8171fc679bec/s02e02_tmp.png")
#    print(text)
#    text = ocr_with_doctr("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCQ2dDSmdVPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--fefb459c3b32582ee9a2750b7b59a565d8d19d0a/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNIYVFMUUIya0MwQWM2Q25OaGRtVnlld1k2Q25OMGNtbHdWQT09IiwiZXhwIjpudWxsLCJwdXIiOiJ2YXJpYXRpb24ifX0=--ced9b89e636fbe4e9d139673c30ec65b0d14eccd/2_Zagubiona_karta_A4_CMYK_jedostronna_druk_040425-1.png")
#    print(text)
#    text = ocr_with_doctr("C:\\Users\\Elzab\\Downloads\\va0zd92mygxjyo80gw68n56op6ii.jpg")
#    print(text.render())
   ocr_image("https://app.circle.so/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBCTjg0eVFNPSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--9abb7ecf713338215b2b729091cb28bc97943c5b/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdDRG9MWm05eWJXRjBTU0lJY0c1bkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNITUdrQ09BUTZDbk5oZG1WeWV3WTZDbk4wY21sd1ZBPT0iLCJleHAiOm51bGwsInB1ciI6InZhcmlhdGlvbiJ9fQ==--cfda350175ba87e768b4e96e935a8171fc679bec/andrzej_tmp.png")