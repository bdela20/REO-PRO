import os
from dotenv import load_dotenv

load_dotenv()

print("API Key:", os.getenv('RAPIDAPI_KEY'))
print("Key exists:", os.getenv('RAPIDAPI_KEY') is not None)
