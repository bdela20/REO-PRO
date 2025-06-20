import requests

url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"

payload = {
    "limit": 2,
    "city": "Austin",
    "state_code": "TX",
    "status": ["for_sale"]
}

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "e9214afa06msh86467c0eade99b6p1bba92jsnb7f23f8c2940",
    "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:200]}...")
