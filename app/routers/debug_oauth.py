#!/usr/bin/env python3
"""
Debug script to check OAuth configuration
Run this to see what's wrong with Google OAuth setup
"""

import os
from dotenv import load_dotenv

print("🔍 Debugging OAuth Configuration...\n")

# Load environment variables
load_dotenv()

# Check environment variables
print("1. Checking Environment Variables:")
google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

if google_client_id:
    print(f"   ✅ GOOGLE_CLIENT_ID: {google_client_id[:20]}...")
else:
    print("   ❌ GOOGLE_CLIENT_ID: NOT FOUND")

if google_client_secret:
    print(f"   ✅ GOOGLE_CLIENT_SECRET: {google_client_secret[:10]}...")
else:
    print("   ❌ GOOGLE_CLIENT_SECRET: NOT FOUND")

print()

# Check if Authlib is installed
print("2. Checking Authlib Installation:")
try:
    import authlib
    print(f"   ✅ Authlib version: {authlib.__version__}")
except ImportError:
    print("   ❌ Authlib NOT INSTALLED")
    print("   Run: pip install Authlib==1.2.1")

print()

# Test Flask app creation
print("3. Testing Flask App Creation:")
try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Check if OAuth is attached to app
        if hasattr(app, 'oauth'):
            print("   ✅ OAuth attached to app")
            
            # Check if Google client is registered
            try:
                google_client = app.oauth.create_client('google')
                print("   ✅ Google client created successfully")
            except Exception as e:
                print(f"   ❌ Error creating Google client: {e}")
        else:
            print("   ❌ OAuth NOT attached to app")
            
except Exception as e:
    print(f"   ❌ Error creating app: {e}")

print()

# Check .env file contents
print("4. Checking .env File:")
try:
    with open('.env', 'r') as f:
        env_content = f.read()
    
    if 'GOOGLE_CLIENT_ID=' in env_content:
        print("   ✅ GOOGLE_CLIENT_ID found in .env")
    else:
        print("   ❌ GOOGLE_CLIENT_ID missing from .env")
        
    if 'GOOGLE_CLIENT_SECRET=' in env_content:
        print("   ✅ GOOGLE_CLIENT_SECRET found in .env")  
    else:
        print("   ❌ GOOGLE_CLIENT_SECRET missing from .env")
        
except Exception as e:
    print(f"   ❌ Error reading .env: {e}")

print("\n🎯 Next Steps:")
print("   1. If Authlib is missing: pip install Authlib==1.2.1")
print("   2. If Google credentials are missing: update your .env file")
print("   3. If OAuth not attached: check your app/__init__.py")
print("   4. Restart your app after fixing issues")