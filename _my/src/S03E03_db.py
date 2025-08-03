from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
from library import make_json, send_json
import requests
import re

load_dotenv()
client = OpenAI()

task_name = "database"
my_key = os.getenv("MY_KEY")

def send_query(query):
    url = "https://c3ntrala.ag3nts.org/apidb"
    data = { "task": "database", "apikey": my_key, "query": query }
    response = requests.post(url, json=data)
    return response.json()

def create_db_query(tables, tables_create_info):
    user_prompt = f"""Jesteś ekspertem w dziedzinie tworzenia zapytań do bazy danych w języku SQL.
    Twoim zadaniem jest zwrócenie nam numerów ID czynnych datacenter, które zarządzane są przez menadżerów, którzy aktualnie przebywają na urlopie (są nieaktywni). To pozwoli nam lepiej wytypować centra danych bardziej podatne na atak. Nazwa zadania to database.
    W bazie danych są tabeli: {tables}
    Oto informacje o tabelach: {tables_create_info}
    Zwróć tylko zapytanie SQL, bez dodatkowych informacji.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    return answer

if __name__ == "__main__":
    # tables = str(send_query("show tables").get("reply"))
    # print(tables)
    # # show create table NAZWA_TABELI / {'reply': [{'Tables_in_banan': 'connections'}, {'Tables_in_banan': 'correct_order'}, {'Tables_in_banan': 'datacenters'}, {'Tables_in_banan': 'users'}], 'error': 'OK'}
    # users = str(send_query("show create table users").get("reply")[0])
    # connections = str(send_query("show create table connections").get("reply")[0])
    # correct_order = str(send_query("show create table correct_order").get("reply")[0])
    # datacenters = str(send_query("show create table datacenters").get("reply")[0])
    # tables_create_info = f"""
    # {users}
    # {connections}
    # {correct_order}
    # {datacenters}
    # """
    # print(tables_create_info)
    # query = create_db_query(tables, tables_create_info)
    # # print(query)
    # # regex form ```sql\n(.*)\n```
    # # query = re.search(r"```sql\n(.*)\n```", query).group(1)
    # print(query)
    # # remove ```sql\n and \n```
    # query = query.replace("```sql\n", "").replace("\n```", "")
    # answer = send_query(query).get("reply")
    # dc_ids = []
    # for dc in answer:
    #     dc_ids.append(dc.get("dc_id"))
    # print(dc_ids)
    # print(send_json({"task": task_name, "apikey": my_key, "answer": dc_ids}))
    correct_order = send_query("select * from correct_order").get("reply")
    #sort by weight
    correct_order.sort(key=lambda x: int(x.get("weight")), reverse=False)
    for letter in correct_order:
        print(letter.get("letter"), end="")
    print()