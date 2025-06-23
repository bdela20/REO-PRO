#!/usr/bin/env python3
"""
Minimal Working PropInsight with Real API Integration
"""

from flask import Flask, render_template_string, request, jsonify
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PropInsight - Real Estate Analytics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #1e40af; font-size: 2.5em; margin-bottom: 10px; }
        .status { background: #10b981; color: white; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .search-container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .search-form { display: flex; gap: 15px; align-items: end; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #374151; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #3b82f6; }
        .search-btn { background: #3b82f6; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .search-btn:hover { background: #2563eb; }
        .search-btn:disabled { background: #9ca3af; cursor: not-allowed; }
        .results { display: none; }
        .demographics { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .demographics h2 { color: #1e40af; margin-bottom: 20px; }
        .demo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .demo-item { text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px; }
        .demo-item .value { font-size: 1.5em; font-weight: bold; color: #1e40af; }
        .demo-item .label { color: #6b7280; margin-top: 5px; }
        .properties { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .property-card { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 20px; }
        .property-card h3 { color: #1e40af; margin-bottom: 10px; }
        .property-info { margin-bottom: 10px; }
        .property-info .label { font-weight: 600; color: #374151; }
        .property-info .value { color: #6b7280; }
        .error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .loading { text-align: center; padding: 40px; color: #6b7280; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 PropInsight</h1>
            <p>Real Estate Analytics Platform</p>
        </div>

        <div class="status">
            🔥 PropInsight LIVE - Real Estate Data Powered by RentCast & Census APIs
        </div>

        <div class="search-container">
            <div class="search-form">
                <div class="form-group">
                    <label for="location">Location (City, State)</label>
                    <input type="text" id="location" placeholder="e.g., Austin, TX" value="Austin, TX">
                </div>
                <button class="search-btn" id="searchBtn" onclick="searchProperties()">🔍 Search Properties</button>
            </div>
        </div>

        <div id="error" class="error" style="display: none;"></div>
        <div id="loading" class="loading" style="display: none;">🔍 Searching for properties and demographics...</div>
        
        <div id="results" class="results">
            <div id="demographics" class="demographics"></div>
            <div id="properties" class="properties"></div>
        </div>
    </div>

    <script>
        async function searchProperties() {
            const location = document.getElementById('location').value.trim();
            const searchBtn = document.getElementById('searchBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const error = document.getElementById('error');
            
            if (!location) {
                showError('Please enter a location');
                return;
            }

            // Show loading state
            searchBtn.disabled = true;
            searchBtn.textContent = '🔍 Searching...';
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location: location })
                });

                if (!response.ok) {
                    throw new Error(`Request failed with status code ${response.status}`);
                }

                const data = await response.json();
                displayResults(data);
                
            } catch (err) {
                console.error('Search error:', err);
                showError(`❌ Network error: ${err.message}`);
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = '🔍 Search Properties';
                loading.style.display = 'none';
            }
        }

        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.style.display = 'block';
            document.getElementById('results').style.display = 'none';
        }

        function displayResults(data) {
            const demographics = data.demographics;
            const properties = data.properties;
            const searchInfo = data.search_info;

            // Display demographics
            const demoHtml = `
                <h2>📊 Demographics for ${searchInfo.location}</h2>
                <div class="demo-grid">
                    <div class="demo-item">
                        <div class="value">${demographics.population}</div>
                        <div class="label">Population</div>
                    </div>
                    <div class="demo-item">
                        <div class="value">${demographics.median_income}</div>
                        <div class="label">Median Income</div>
                    </div>
                    <div class="demo-item">
                        <div class="value">${demographics.median_home_value}</div>
                        <div class="label">Median Home Value</div>
                    </div>
                    <div class="demo-item">
                        <div class="value">${demographics.unemployment_rate}</div>
                        <div class="label">Unemployment Rate</div>
                    </div>
                </div>
                <p style="margin-top: 15px; color: #6b7280; font-size: 0.9em;">
                    📡 Data source: ${searchInfo.data_source} | Found ${searchInfo.properties_found} properties
                </p>
            `;
            document.getElementById('demographics').innerHTML = demoHtml;

            // Display properties
            const propertiesHtml = properties.map(property => `
                <div class="property-card">
                    <h3>${property.address}</h3>
                    <div class="property-info">
                        <span class="label">Rent Estimate:</span>
                        <span class="value">$${property.rent_estimate}</span>
                    </div>
                    <div class="property-info">
                        <span class="label">Bedrooms:</span>
                        <span class="value">${property.bedrooms}</span>
                    </div>
                    <div class="property-info">
                        <span class="label">Bathrooms:</span>
                        <span class="value">${property.bathrooms}</span>
                    </div>
                    <div class="property-info">
                        <span class="label">Square Feet:</span>
                        <span class="value">${property.square_feet}</span>
                    </div>
                </div>
            `).join('');
            document.getElementById('properties').innerHTML = propertiesHtml;

            document.getElementById('results').style.display = 'block';
            document.getElementById('error').style.display = 'none';
        }

        // Allow Enter key to search
        document.getElementById('location').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProperties();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test', methods=['GET'])
def test_services():
    """Test endpoint to check if services can be imported"""
    try:
        print("🧪 Testing service imports...")
        from app.services import PropertyService, DemographicsService
        print("✅ Services imported successfully!")
        
        # Test creating services
        prop_service = PropertyService()
        demo_service = DemographicsService()
        print("✅ Services created successfully!")
        
        return jsonify({
            'status': 'success',
            'message': 'Services import and create successfully!',
            'services': ['PropertyService', 'DemographicsService']
        })
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/search', methods=['POST'])
def search_properties():
    print("🔍 Search endpoint called")
    try:
        data = request.get_json()
        location = data.get('location', '').strip()
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Parse location (City, State)
        parts = [p.strip() for p in location.split(',')]
        city = parts[0]
        state = parts[1] if len(parts) > 1 else 'CA'
        
        print(f"🔍 Searching for properties in {city}, {state}")
        
        # Try to import and use real services
        try:
            print("📦 Importing services...")
            from app.services import PropertyService, DemographicsService
            print("✅ Services imported successfully")
            
            # Get real property data
            print("🏠 Getting property data...")
            property_service = PropertyService()
            properties = property_service.search_properties(city, state, limit=8)
            print(f"✅ Found {len(properties)} properties")
            
            # Get real demographics data
            print("📊 Getting demographics data...")
            demographics_service = DemographicsService()
            demographics = demographics_service.get_demographics_by_city(city, state)
            print(f"✅ Got demographics: population={demographics.get('total_population', 'N/A')}")
            
            # Format response with real data
            result = {
                'properties': properties,
                'demographics': {
                    'population': f"{demographics.get('total_population', 0):,}" if demographics.get('total_population') else 'N/A',
                    'median_income': f"${demographics.get('median_household_income', 0):,.0f}" if demographics.get('median_household_income') else 'N/A',
                    'median_home_value': f"${demographics.get('median_home_value', 0):,.0f}" if demographics.get('median_home_value') else 'N/A',
                    'unemployment_rate': f"{demographics.get('unemployment_rate', 0):.1f}%" if demographics.get('unemployment_rate') else 'N/A'
                },
                'search_info': {
                    'location': f"{city}, {state}",
                    'properties_found': len(properties),
                    'data_source': 'RentCast + US Census Bureau'
                }
            }
            
            print(f"✅ Returning result with {len(properties)} properties")
            return jsonify(result)
            
        except ImportError as ie:
            print(f"❌ Import error: {str(ie)}")
            # Fallback to demo data if services can't be imported
            result = {
                'properties': [
                    {
                        'address': '123 Demo St, ' + city,
                        'rent_estimate': 2500.0,
                        'bedrooms': 3,
                        'bathrooms': 2,
                        'square_feet': 1200
                    },
                    {
                        'address': '456 Sample Ave, ' + city,
                        'rent_estimate': 2800.0,
                        'bedrooms': 4,
                        'bathrooms': 3,
                        'square_feet': 1400
                    }
                ],
                'demographics': {
                    'population': 'Demo Data',
                    'median_income': 'Demo Data',
                    'median_home_value': 'Demo Data',
                    'unemployment_rate': 'Demo Data'
                },
                'search_info': {
                    'location': f"{city}, {state}",
                    'properties_found': 2,
                    'data_source': 'Demo Mode - Services Import Failed'
                }
            }
            return jsonify(result)
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Minimal PropInsight Web Application...")
    print("📱 Open your browser to: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
