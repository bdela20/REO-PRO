#!/usr/bin/env python3
"""
PropInsight API Data Exploration
Analyzes RentCast and Census API responses to design optimal database structure
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

class PropInsightDataAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize API credentials
        self.rentcast_key = os.getenv('RENTCAST_API_KEY')
        self.census_key = os.getenv('CENSUS_API_KEY', '')  # Census works without key
        
        # API endpoints
        self.rentcast_base = "https://api.rentcast.io/v1"
        self.census_base = "https://api.census.gov/data/2022/acs/acs5"
        
        # Request headers
        self.rentcast_headers = {
            "X-API-Key": self.rentcast_key,
            "Content-Type": "application/json"
        }
    
    def analyze_rentcast_property_structure(self):
        """Analyze RentCast property data structure with a single test call"""
        print("🏠 ANALYZING RENTCAST PROPERTY DATA STRUCTURE")
        print("=" * 60)
        
        # Test with a well-known address
        test_address = "1600 Amphitheatre Parkway, Mountain View, CA"
        print(f"📍 Test Address: {test_address}")
        
        try:
            # Make API call
            response = requests.get(
                f"{self.rentcast_base}/properties",
                headers=self.rentcast_headers,
                params={"address": test_address},
                timeout=15
            )
            
            print(f"🌐 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully retrieved property data")
                
                # Display the raw response
                print("\n📄 Raw API Response:")
                print(json.dumps(data, indent=2))
                
                # Analyze structure
                if isinstance(data, list) and len(data) > 0:
                    property_record = data[0]
                    self._analyze_property_fields(property_record)
                elif isinstance(data, dict):
                    self._analyze_property_fields(data)
                else:
                    print("⚠️ Unexpected data format received")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Error Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    def _analyze_property_fields(self, property_data):
        """Analyze individual property fields for database design"""
        print("\n🔍 PROPERTY FIELD ANALYSIS:")
        print("-" * 40)
        
        field_analysis = []
        
        for field_name, field_value in property_data.items():
            field_type = type(field_value).__name__
            sample_value = str(field_value)[:50]
            
            # Determine SQL data type
            sql_type = self._determine_sql_type(field_value, field_name)
            
            field_analysis.append({
                'field': field_name,
                'python_type': field_type,
                'sql_type': sql_type,
                'sample': sample_value
            })
            
            print(f"   {field_name:20} | {field_type:10} | {sql_type:20} | {sample_value}")
        
        return field_analysis
    
    def _determine_sql_type(self, value, field_name):
        """Determine appropriate SQL data type based on field value and name"""
        if value is None:
            return "TEXT"
        
        # Specific field mappings
        field_mappings = {
            'id': 'SERIAL PRIMARY KEY',
            'latitude': 'DECIMAL(10,8)',
            'longitude': 'DECIMAL(11,8)',
            'bedrooms': 'INTEGER',
            'bathrooms': 'DECIMAL(3,1)',
            'squareFootage': 'INTEGER',
            'yearBuilt': 'INTEGER',
            'lotSize': 'DECIMAL(10,2)',
            'estimatedValue': 'DECIMAL(12,2)',
            'rentEstimate': 'DECIMAL(8,2)'
        }
        
        if field_name in field_mappings:
            return field_mappings[field_name]
        
        # Type-based mappings
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "DECIMAL(10,2)"
        elif isinstance(value, str):
            if len(value) <= 50:
                return f"VARCHAR({max(50, len(value) * 2)})"
            else:
                return "TEXT"
        else:
            return "TEXT"
    
    def analyze_census_demographic_structure(self):
        """Analyze Census API demographic data structure"""
        print("\n\n👥 ANALYZING CENSUS DEMOGRAPHIC DATA STRUCTURE")
        print("=" * 60)
        
        # Test census query for Austin, TX area
        test_params = {
            "get": "B01003_001E,B19013_001E,B15003_022E,NAME",  # Population, Income, Education
            "for": "county:453",  # Travis County (Austin)
            "in": "state:48",     # Texas
            "key": self.census_key
        }
        
        print("📊 Test Query: Population, Income, and Education data for Travis County, TX")
        
        try:
            response = requests.get(
                self.census_base,
                params=test_params,
                timeout=15
            )
            
            print(f"🌐 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully retrieved demographic data")
                
                # Display raw response
                print("\n📄 Raw Census Response:")
                print(json.dumps(data, indent=2))
                
                # Analyze census data structure
                if len(data) >= 2:
                    headers = data[0]
                    sample_data = data[1]
                    self._analyze_census_fields(headers, sample_data)
                else:
                    print("⚠️ Insufficient census data received")
                    
            else:
                print(f"❌ Census API Error: {response.status_code}")
                print(f"📄 Error Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    def _analyze_census_fields(self, headers, sample_data):
        """Analyze census field structure"""
        print("\n🔍 CENSUS FIELD ANALYSIS:")
        print("-" * 40)
        
        # Map census variable codes to human names
        field_mappings = {
            'B01003_001E': 'total_population',
            'B19013_001E': 'median_household_income',
            'B15003_022E': 'bachelors_degree_count',
            'NAME': 'area_name'
        }
        
        for i, (header, value) in enumerate(zip(headers, sample_data)):
            field_name = field_mappings.get(header, header)
            
            # Determine data type
            if value and str(value).replace('-', '').replace('.', '').isdigit():
                data_type = "INTEGER" if '.' not in str(value) else "DECIMAL(12,2)"
            else:
                data_type = "TEXT"
            
            print(f"   {field_name:25} | {header:15} | {data_type:15} | {value}")
    
    def generate_database_schema_recommendations(self):
        """Generate recommended database schema based on API analysis"""
        print("\n\n🗄️ DATABASE SCHEMA RECOMMENDATIONS")
        print("=" * 60)
        
        schema_recommendations = """
        Based on API analysis, here are the recommended database tables:
        
        1. PROPERTIES TABLE:
           - Primary storage for RentCast property data
           - Key fields: address, city, state, bedrooms, bathrooms, estimated_value
           - Indexes needed: location (city/state), price range, property size
        
        2. DEMOGRAPHICS TABLE:
           - Census demographic data by geographic area
           - Key fields: state_code, county_code, population, income, education
           - Links to properties via geographic codes
        
        3. MARKET_TRENDS TABLE:
           - Historical market data and trends
           - Time-series data for price and rent changes
        
        4. SEARCH_HISTORY TABLE:
           - Track user searches for analytics
           - Cache popular search results
        """
        
        print(schema_recommendations)
    
    def run_complete_analysis(self):
        """Execute complete data structure analysis"""
        print("🚀 PROPINSIGHT DATA STRUCTURE ANALYSIS")
        print("=" * 80)
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Verify API keys
        if not self.rentcast_key:
            print("❌ ERROR: RENTCAST_API_KEY not found in .env file")
            print("💡 Please ensure your .env file contains the RentCast API key")
            return False
        
        print(f"✅ RentCast API Key loaded: {self.rentcast_key[:8]}...")
        
        if self.census_key:
            print(f"✅ Census API Key loaded: {self.census_key[:8]}...")
        else:
            print("⚠️ Census API Key not found (will use without key)")
        
        # Run analyses
        self.analyze_rentcast_property_structure()
        self.analyze_census_demographic_structure()
        self.generate_database_schema_recommendations()
        
        print("\n" + "=" * 80)
        print("🎉 DATA STRUCTURE ANALYSIS COMPLETE!")
        print("✅ Next Steps:")
        print("   1. Review the API response structures above")
        print("   2. Create database schema based on findings")
        print("   3. Build Flask models to match the schema")
        print("   4. Implement API integration layer")
        print("=" * 80)
        
        return True

# Main execution
if __name__ == "__main__":
    analyzer = PropInsightDataAnalyzer()
    analyzer.run_complete_analysis()