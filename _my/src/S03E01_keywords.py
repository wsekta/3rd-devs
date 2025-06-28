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

load_dotenv()
client = OpenAI()

task_name = "dokumenty"

def files_list_generator(directory):
    for file in sorted(os.listdir(directory)):
        if file.endswith(".txt"):
            yield file
    return

def who_is_fact_about(fact):
    system_prompt = f"""Jesteś ekspertem w dziedzinie analizy raportów z fabryki.
    Twoim zadaniem jest ustalenie kogo lub jakiego miejsca dotyczy raport.
    Zwróć tylko jedną osobę lub miejsce które dotyczy raport - imię i nazwisko, ksywkę, lub nazwę miejsca.
    """
    user_prompt = f"""
    Raport: {fact}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    return answer

def process_fact(who, fact):
    system_prompt = f"""Jesteś ekspertem w dziedzinie słów kluczowych na podstawie raportów z fabryki.
    Twoim zadaniem jest wygenerowanie słów kluczowych dla podanego tekstu.
    Słowa kluczowe powinny być w języku polskim.
    Muszą być w mianowniku (np. "nauczyciel", "programista", a nie "nauczyciela", "programistów").
    Słowa powinny być oddzielone przecinkami (np. słowo1,słowo2,słowo3).
    słowa mają być związane z osobą lub miejscem wymienionym w raporcie.
    <example>
    Raport: Sektor G jest sektorem produkcyjnym.
    Odpowiedź: sektor G, produkcja
    </example>
    <example>
    Raport: Jan Kowalski jest nauczycielem matematyki. Zna język programowania Python.
    Odpowiedź: nauczyciel, matematyka, Python, Jan Kowalski
    </example>
    """
    user_prompt = f"""
    Raport: {fact}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    return answer

def generate_context():
    if os.path.exists(os.path.join(os.path.dirname(__file__), "tmp", "context.json")):
        with open(os.path.join(os.path.dirname(__file__), "tmp", "context.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    directory = os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki", "facts")
    facts = {}
    for file in files_list_generator(directory):
        fact = ""
        with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
            fact = f.read()
        who = who_is_fact_about(fact)
        keywords = process_fact(who, fact)
        facts[who] = {"keywords": keywords, "fact": fact}
        
    with open(os.path.join(os.path.dirname(__file__), "tmp", "context.json"), "w", encoding="utf-8") as f:
        json.dump(facts, f)
    return facts

def is_fact_about(report_name, report, who):
    system_prompt = f"""Jesteś ekspertem w dziedzinie analizy raportów z fabryki.
    Twoim zadaniem jest ustalenie czy raport dotyczy podanej osoby lub miejsca.
    Zwróć uwage czy osoba lub miejsce jest wymienione w raporcie lub w jego nazwie.
    Zwróć tylko jedną odpowiedź - "tak" lub "nie".
    <example>
    Nazwa raportu: 2024-11-12_report-06-sektor_C2.txt
    Raport: report...
    Osoba lub miejsce: Sektor C
    Odpowiedź: tak
    </example>
    <example>
    Nazwa raportu: 2024-11-12_report-02-sektor_A3.txt
    Raport: report...
    Osoba lub miejsce: Sektor A
    Odpowiedź: tak
    </example>
    <example>
    Nazwa raportu: 2024-11-12_report-02-sektor_A3.txt
    Raport: report...
    Osoba lub miejsce: Sektor C
    Odpowiedź: nie
    </example>
    """
    user_prompt = f"""
    Nazwa raportu: {report_name}
    Raport: {report}
    Osoba lub miejsce: {who}
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    return answer.strip() == "tak"

def generate_context_for_report(report_name, context):
    with open(os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki", report_name), "r", encoding="utf-8") as f:
        report = f.read()
    context_for_report = ""
    keywords = ""
    for who, data in context.items():
        if is_fact_about(report_name, report, who):
            context_for_report += f"<person_or_place>\n<name>{who}</name>\n<keywords>{data['keywords']}</keywords>\n<fact>{data['fact']}</fact>\n</person_or_place>\n"
            keywords += f"{data['keywords']},"
    return {"context": context_for_report, "keywords": keywords}

def generate_context_for_all_reports(context):
    if os.path.exists(os.path.join(os.path.dirname(__file__), "tmp", "context_for_all_reports.json")):
        with open(os.path.join(os.path.dirname(__file__), "tmp", "context_for_all_reports.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    context_for_all_reports = {}
    for file in files_list_generator(os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki")):
        context_for_all_reports[file] = generate_context_for_report(file, context)
    with open(os.path.join(os.path.dirname(__file__), "tmp", "context_for_all_reports.json"), "w", encoding="utf-8") as f:
        json.dump(context_for_all_reports, f)
    return context_for_all_reports

def generate_keywords(report_name, keywords):
    with open(os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki", report_name), "r", encoding="utf-8") as f:
        report = f.read()
    system_prompt = f"""Jesteś generatorem słów kluczowych.
    Twoim zadaniem jest wygenerowanie słów kluczowych dla podanego raportu.
    Słowa kluczowe powinny być w języku polskim.
    Uwzględnij informacje z nazwy raportu takie jak nazwa sektoru np. sektor A, sektor B, sektor C itp.
    Muszą być w mianowniku (np. "nauczyciel", "programista", a nie "nauczyciela", "programistów").
    Słowa powinny być oddzielone przecinkami (np. słowo1,słowo2,słowo3).
    Używaj precyzyjnych acz ogólnych słów kluczowych - jeśli raport wspomina o "dzikiej faunie", "zwierzynie leśnej" lub "wildlife", system walidujący prawdopodobnie oczekuje ogólniejszego słowa kluczowego, np. "zwierzęta"
    """
    user_prompt = f"""
    Nazwa raportu: {report_name}
    Raport: {report}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    # get answer from <answer> tag by using regex
    # answer = re.search(r"<answer>\n?(.*?)\n?</answer>", answer).group(1)

    sum_prompt = f"""Jesteś ekspertem w łączeniu słów kluczowych.
    Dostaniesz dwie listy słów kluczowych.
    Twoim zadaniem jest połączenie tych list w jedną.
    Uwzględnij wszystkie słowa kluczowe z obu list.
    Zadbaj o jakość słów kluczowych:
    - język polski, mianownik, oddzielone przecinkiem. To podstawa.
    - Konkretność: Staraj się, aby słowa kluczowe były jak najbardziej specyficzne dla danego raportu i powiązanych faktów. 
    - "Zwierzęta": Jeśli raport wspomina o "dzikiej faunie", "zwierzynie leśnej" lub "wildlife", system walidujący prawdopodobnie oczekuje ogólniejszego słowa kluczowego, np. "zwierzęta".
    - Nazwiska i imiona: Powinny być uwzględnione, jeśli są istotne.

    Słowa kluczowe powinny być oddzielone przecinkami (np. słowo1,słowo2,słowo3).
    """
    user_prompt = f"""
    Słowa kluczowe z raportu: {answer}
    Słowa kluczowe z kontekstu: {keywords}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": sum_prompt}, {"role": "user", "content": user_prompt}],
    )
    answer = response.choices[0].message.content
    print(report_name, answer)
    return answer
    
if __name__ == "__main__":
    directory = os.path.join(os.path.dirname(__file__), "data", "pliki_z_fabryki")
    context = generate_context()
    context_for_all_reports = generate_context_for_all_reports(context)
    keywords = {}
    for file in files_list_generator(directory):
        keywords[file] = generate_keywords(file, context_for_all_reports[file]["keywords"])
    print(keywords)
    json_data = make_json(task_name, keywords)
    result = send_json(json_data)
    print(result)
        