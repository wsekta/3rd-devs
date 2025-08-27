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
import argparse

load_dotenv()
client = OpenAI()

my_key = os.getenv("MY_KEY")
task_name = "research"

def prepare_jsonl_data(file_name, value):
    """prepare jsonl file for training"""
    jsonl_data = []
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            jsonl_data.append({"prompt": line.rstrip(), "completion": value})
    return jsonl_data

def create_jsonl_file(jsonl_data, file_name):
    """create jsonl file"""
    with open(file_name, "w", encoding="utf-8") as f:
        for item in jsonl_data:
            text_line = '{"messages":[{"role":"system","content":"validate data"},{"role":"user","content":' + f'"{item["prompt"]}"' + '},{"role":"assistant","content":' + f'"{item["completion"]}"' + '}]}\n'
            f.write(text_line)

def use_fine_tuned_model(data):
    """use fine-tuned model to evaluate data"""
    response = client.chat.completions.create(
        model="ft:gpt-4.1-mini-2025-04-14:personal:ai-devs3:C6zjXSdI",
        messages=[
            {"role": "system", "content": "validate data"},
            {"role": "user", "content": data}
        ]
    )
    answer = response.choices[0].message.content
    print(f"Data: {data}")
    print(f"Answer: {answer}")
    return answer == "1"

if __name__ == "__main__":
    # Argument parser for mutually exclusive flags --prepare and --eval
    parser = argparse.ArgumentParser(description="Research script for data preparation and evaluation.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true', help='Prepare training data')
    group.add_argument('--eval', action='store_true', help='Evaluate on fine-tuned model')
    args = parser.parse_args()

    if args.prepare:
        correct_data = prepare_jsonl_data("_my/src/data/lab_data/correct.txt", 1)
        incorrect_data = prepare_jsonl_data("_my/src/data/lab_data/incorect.txt", 0)
        jsonl_data = correct_data + incorrect_data
        create_jsonl_file(jsonl_data, "_my/src/data/lab_data/data.jsonl")
    elif args.eval:
        correct_rows = []
        with open("_my/src/data/lab_data/verify.txt", "r", encoding="utf-8") as f:
            for line in f:
                data = line.rstrip()[3:]
                if use_fine_tuned_model(data):
                    print(f"Data: {data} is correct")
                    correct_rows.append(line[:2])
                else:
                    print(f"Data: {data} is incorrect")
        jsonl_data = make_json(task_name, correct_rows)
        response = send_json(jsonl_data)
        print(response)
    else:
        print("Invalid argument")