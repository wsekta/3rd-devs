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

id_number = 0

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

def add_vector(vector, metadata):
    # add static variable to store id number for each vector
    global id_number
    id_number += 1
    vector_client.upsert(
        collection_name=VECTOR_COLLECTION_NAME,
        points=[PointStruct(vector=vector, payload=metadata, id=id_number)],
    )

def prepare_database():
    #for all files in _my/src/data/do-not-share
    for file in os.listdir("_my/src/data/do-not-share"):
        with open(f"_my/src/data/do-not-share/{file}", "r") as f:
            text = f.read()
            vector = embed_text(text)
            add_vector(vector, {"source": file})

def search_vector(query):
    vector = embed_text(query)
    results = vector_client.search(
        collection_name=VECTOR_COLLECTION_NAME,
        query_vector=vector,
        limit=1,
    )
    return results

def filename_to_date(filename):
    # filename is in format YYYY_MM_DD.txt date is in format YYYY-MM-DD
    return filename.split("_")[0] + "-" + filename.split("_")[1] + "-" + filename.split("_")[2].split(".")[0]

if __name__ == "__main__":
    vector_client = QdrantClient(url=VECTOR_DATABASE_URL)
    create_collection()
    # prepare_database()
    prompt = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    results = search_vector(prompt)
    date = filename_to_date(results[0].payload["source"])
    print(date)
    json_data = make_json(task_name, date)
    print(send_json(json_data))


