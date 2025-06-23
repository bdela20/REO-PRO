from flask import Flask, render_template_string, request, jsonify
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services import PropertyService
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    print("⚠️  Services not available yet - running in demo mode")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Simple HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PropInsight - Smart Property Analytics</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.2/axios.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            font-size: 3rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }
        .search-form {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .search-input {
            flex: 1;
            min-width: 300px;
            padding: 15px;
            font-size: 1.1rem;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            outline: none;
        }
        .search-input:focus {
            border-color: #667eea;
        }
        .search-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .search-button:hover {
            transform: translateY(-2px);
        }
        .search-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 1.2rem;
            padding: 40px;
        }
        .error {
            background: #fee2e2;
            color: #dc2626;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .success {
            background: #d1fae5;
            color: #065f46;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .property-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .property-card h4 {
            color: #1f2937;
            margin-bottom: 15px;
        }
        .property-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .property-details p {
            margin: 5px 0;
            padding: 8px;
            background: #f8fafc;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">🏠 PropInsight</h1>
            <p>Smart Property Analytics & Market Intelligence</p>
            <p style="color: #6b7280; font-size: 0.9rem;">
                🔍 Real-time property data • 📊 Market demographics • 🎯 Investment insights
            </p>
        </div>
        
        <form id="searchForm" class="search-form">
            <input 
                id="searchInput" 
                type="text" 
                class="search-input" 
                placeholder="Search by address or city (e.g., 'Austin, TX')"
                required
            />
            <button type="submit" class="search-button" id="searchButton">
                Search Properties
            </button>
        </form>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('searchInput').value.trim();
            const results = document.getElementById('results');
            const button = document.getElementById('searchButton');
            
            if (!query) return;
            
            // Update UI
            button.disabled = true;
            button.textContent = 'Searching...';
            results.innerHTML = '<div class="loading">🔍 Searching properties...</div>';
            
            try {
                const response = await axios.post('/api/search', 
                    { query }, 
                    { headers: { 'Content-Type': 'application/json' } }
                );
                
                if (response.data.success) {
                    const data = response.data.results;
                    let html = `<div class="success">
                        <h3>🎉 Found ${data.properties?.length || 0} properties</h3>
                    </div>`;
                    
                    if (data.properties && data.properties.length > 0) {
                        data.properties.forEach(prop => {
                            html += `
                                <div class="property-card">
                                    <h4>📍 ${prop.address || 'Address not available'}</h4>
                                    <div class="property-details">
                                        <p><strong>💰 Price:</strong> $${(prop.estimated_value || prop.rent_estimate || 'N/A')}</p>
                                        <p><strong>🛏️ Bedrooms:</strong> ${prop.bedrooms || 'N/A'}</p>
                                        <p><strong>🚿 Bathrooms:</strong> ${prop.bathrooms || 'N/A'}</p>
                                        <p><strong>📐 Size:</strong> ${prop.square_footage || 'N/A'} sq ft</p>
                                        <p><strong>🏠 Type:</strong> ${prop.property_type || 'N/A'}</p>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    if (data.demographics) {
                        html += `
                            <div class="property-card">
                                <h4>📊 Demographics</h4>
                                <div class="property-details">
                                    <p><strong>👥 Population:</strong> ${data.demographics.total_population || 'N/A'}</p>
                                    <p><strong>💰 Median Income:</strong> $${data.demographics.median_household_income || 'N/A'}</p>
                                    <p><strong>🏘️ Housing Units:</strong> ${data.demographics.total_housing_units || 'N/A'}</p>
                                </div>
                            </div>
                        `;
                    }
                    
                    results.innerHTML = html;
                } else {
                    results.innerHTML = '<div class="error">❌ Search failed. Please try again.</div>';
                }
            } catch (error) {
                results.innerHTML = '<div class="error">❌ Network error: ' + error.message + '</div>';
            } finally {
                button.disabled = false;
                button.textContent = 'Search Properties';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['POST'])
def api_search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if SERVICES_AVAILABLE:
            property_service = PropertyService()
            results = property_service.search_properties(query)
        else:
            # Demo data
            results = {
                'properties': [
                    {
                        'address': f'Demo Property in {query}',
                        'estimated_value': 350010,
                        'bedrooms': 3,
                        'bathrooms': 2,
                        'square_footage': 1500,
                        'property_type': 'Single Family'
                    }
                ],
                'demographics': {
                    'total_population': 50010,
                    'median_household_income': 65001,
                    'total_housing_units': 20000
                }
            }
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results.get('properties', []))
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting PropInsight Web Application...")
    print("📱 Open your browser to: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
