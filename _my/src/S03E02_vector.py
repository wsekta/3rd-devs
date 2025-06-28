from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
from library import make_json, send_json

load_dotenv()
client = OpenAI()

task_name = "wektory"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSION = 3072
VECTOR_DATABASE_URL = "http://localhost:6333"
VECTOR_COLLECTION_NAME = "S03E02_vector"

def embed_text(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding

vector_client = None

def create_collection():
    if not vector_client.collection_exists(VECTOR_COLLECTION_NAME):
        vector_client.create_collection(
            collection_name=VECTOR_COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
        )
    else:
        print(f"Collection {VECTOR_COLLECTION_NAME} already exists")

def add_

if __name__ == "__main__":
    vector_client = QdrantClient(url=VECTOR_DATABASE_URL)
    create_collection()
    text = "test"
    vector = embed_text(text)
    print(f"Vector size: {len(vector)}")
    print(f"Vector: {vector}")
