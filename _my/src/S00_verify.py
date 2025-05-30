import requests

def get_data():
    # URL to fetch data from
    url = "https://poligon.aidevs.pl/dane.txt"
    
    try:
        # Make GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the text content and split it into lines
        data = response.text.strip().split('\n')
        
        return data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
def make_json(data):
    json_data = {
        "task": "POLIGON",
        "apikey": "da6205a3-9e11-43b8-abae-180bd76be80f",
        "answer": data
    }
    return json_data

def send_json(json_data):
    url = "https://poligon.aidevs.pl/verify"
    response = requests.post(url, json=json_data)
    return response.json()

if __name__ == "__main__":
    # Get and print the data
    lines = get_data()
    print("Pobrane dane:")
    for line in lines:
        print(line)
    json_data = make_json(lines)
    response = send_json(json_data)
    print(response)