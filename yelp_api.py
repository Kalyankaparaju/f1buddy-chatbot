import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YELP_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://api.yelp.com/v3/businesses/search"

def search_places(term, location, price="1", limit=5):
    params = {
        "term": term,
        "location": location,
        "price": price,  # 1 = cheapest
        "limit": limit
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get("businesses", [])
    else:
        print("Error:", response.status_code, response.text)
        return []
