import requests

url = "https://api.census.gov/data/2022/acs/acs5"
params = {
    "get": "B01003_001E,B19013_001E,NAME",
    "for": "county:453",
    "in": "state:48"
}

response = requests.get(url, params=params, timeout=15)
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"JSON Data: {data}")
    except Exception as e:
        print(f"JSON Parse Error: {e}")
