#!/usr/bin/env python3
"""
RentCast API Test Script for PropInsight
Tests connection and basic functionality
"""

import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rentcast_connection():
    """Test basic RentCast API connection"""
    print("🏠 Testing RentCast API Connection...")
    print("=" * 50)
    
    api_key = os.getenv('RENTCAST_API_KEY')
    if not api_key:
        print("❌ ERROR: RENTCAST_API_KEY not found in .env file")
        print("   Please add your RentCast API key to the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test API connection with a simple property lookup
    base_url = "https://api.rentcast.io/v1"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Get property details for a known address
        print("\n📍 Test 1: Property Details Lookup")
        endpoint = f"{base_url}/properties"
        params = {
            "address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "propertyType": "Single Family"
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Property lookup successful!")
            print(f"   📊 Response preview: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"   ⚠️  Response: {response.text[:200]}")
        
        # Test 2: Get rent estimate
        print("\n💰 Test 2: Rent Estimate")
        endpoint = f"{base_url}/avm/rent"
        params = {
            "address": "123 Main St, San Francisco, CA",
            "propertyType": "Single Family",
            "bedrooms": 3,
            "bathrooms": 2,
            "squareFootage": 1500
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Rent estimate successful!")
            print(f"   📊 Response preview: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"   ⚠️  Response: {response.text[:200]}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all RentCast API tests"""
    print("🚀 RentCast API Test Suite")
    print("=" * 50)
    print("Testing PropInsight integration with RentCast API\n")
    
    # Test connection
    success = test_rentcast_connection()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ RentCast API: READY FOR PROPINSIGHT!")
        print("🎉 You can proceed to Census API testing")
    else:
        print("❌ RentCast API: NEEDS ATTENTION")
        print("🔧 Check your API key and network connection")
    print("=" * 50)

if __name__ == "__main__":
    main()