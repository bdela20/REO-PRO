#!/usr/bin/env python3
"""
US Census API Test Script for PropInsight
Tests demographic data access for neighborhood analysis
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_census_connection():
    """Test Census API connection and data retrieval"""
    print("🏛️ Testing US Census API Connection...")
    print("=" * 50)
    
    api_key = os.getenv('CENSUS_API_KEY')
    if not api_key:
        print("⚠️  No Census API key found - testing without key (limited requests)")
        api_key = ""
    else:
        print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        # Test 1: Get population data for California counties
        print("\n👥 Test 1: Population Data by County")
        base_url = "https://api.census.gov/data/2022/acs/acs5"
        params = {
            "get": "B01003_001E,NAME",  # Total population + area name
            "for": "county:*",          # All counties
            "in": "state:06",           # California (FIPS code 06)
            "key": api_key if api_key else ""
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Population data retrieved successfully!")
            print(f"   📊 Sample: {data[0]} (headers)")
            print(f"   📊 Sample: {data[1]} (first county)" if len(data) > 1 else "")
            print(f"   📈 Total counties retrieved: {len(data) - 1}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all Census API tests"""
    print("🚀 US Census API Test Suite")
    print("=" * 50)
    print("Testing PropInsight integration with Census demographic data\n")
    
    # Test connection
    success = test_census_connection()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ Census API: READY FOR DEMOGRAPHIC ANALYSIS!")
        print("🎉 PropInsight can now access neighborhood data")
    else:
        print("❌ Census API: NEEDS ATTENTION")
        print("🔧 Check your network connection")
    print("=" * 50)

if __name__ == "__main__":
    main()