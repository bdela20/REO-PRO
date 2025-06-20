import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("CHECKING YOUR OAUTH SETUP")
print("=" * 50)

# Get your values
client_id = os.getenv('GOOGLE_CLIENT_ID')
redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

print(f"\n1. Your Client ID: {client_id}")
print(f"2. Your Redirect URI: {redirect_uri}")

print("\n" + "=" * 50)
print("NOW GO TO GOOGLE CONSOLE")
print("=" * 50)
print("\n1. Go to: https://console.cloud.google.com/apis/credentials")
print("2. Click on your OAuth 2.0 Client ID")
print("3. Make sure these EXACT values are in 'Authorized redirect URIs':")
print(f"   - {redirect_uri}")
print("\n4. If not there, add it and click SAVE")
print("5. Wait 30 seconds for Google to update")