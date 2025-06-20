import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('RENTCAST_API_KEY')
print(f"Testing API Key: {api_key}")

headers = {"X-API-Key": api_key}

url = "https://api.rentcast.io/v1/properties?city=Austin&state=TX&limit=1"
print(f"Testing: {url}")

response = requests.get(url, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:300]}...")

if response.status_code == 401:
    print("❌ 401 = Invalid API Key or Expired")
elif response.status_code == 403:
    print("❌ 403 = Access Forbidden")
elif response.status_code == 200:
    print("✅ 200 = Success!")
