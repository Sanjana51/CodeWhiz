# judge0_api.py
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
}

API_URL = "https://judge0-ce.p.rapidapi.com/submissions"

def submit_code(source_code, language_id, stdin=""):
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin
    }
    response = requests.post(f"{API_URL}?base64_encoded=false&wait=false", json=payload, headers=HEADERS)
    response.raise_for_status()
    token = response.json().get("token")
    return token

def get_submission_result(token):
    result_url = f"{API_URL}/{token}?base64_encoded=false"
    while True:
        res = requests.get(result_url, headers=HEADERS)
        res.raise_for_status()
        result = res.json()
        if result["status"]["id"] in [1, 2]:  # In Queue or Processing
            time.sleep(1)
        else:
            return result
