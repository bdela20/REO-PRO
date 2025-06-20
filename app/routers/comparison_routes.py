# app/routers/comparison_routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

comparison_bp = Blueprint('comparison', __name__, url_prefix='/comparison')

@comparison_bp.route('/')
@login_required
def index():
    """Display the property comparison interface"""
    return render_template('property_comparison.html')

@comparison_bp.route('/api/properties/search')
@login_required
def search_properties():
    """Search for properties to compare"""
    query = request.args.get('q', '')
    
    # In production, search your property database
    # For demo, return sample properties
    properties = [
        {
            'id': 3,
            'address': '789 Pine Road, Lake Mary, FL',
            'price': 525000,
            'beds': 5,
            'baths': 3,
            'sqft': 3200,
            'price_per_sqft': 164,
            'year_built': 2020,
            'days_on_market': 8,
            'image_url': 'https://via.placeholder.com/280x180',
            'mls_number': 'O6234567'
        },
        {
            'id': 4,
            'address': '321 Elm Street, Altamonte Springs, FL',
            'price': 395000,
            'beds': 3,
            'baths': 2,
            'sqft': 2100,
            'price_per_sqft': 188,
            'year_built': 2016,
            'days_on_market': 22,
            'image_url': 'https://via.placeholder.com/280x180',
            'mls_number': 'O6234568'
        },
        {
            'id': 5,
            'address': '555 Beach Boulevard, Orlando, FL',
            'price': 680000,
            'beds': 4,
            'baths': 3.5,
            'sqft': 3500,
            'price_per_sqft': 194,
            'year_built': 2022,
            'days_on_market': 5,
            'image_url': 'https://via.placeholder.com/280x180',
            'mls_number': 'O6234569'
        }
    ]
    
    # Filter based on search query
    if query:
        properties = [p for p in properties if query.lower() in p['address'].lower() or query in p['mls_number']]
    
    return jsonify(properties)

@comparison_bp.route('/api/properties/<int:property_id>')
@login_required
def get_property_details(property_id):
    """Get detailed information for a specific property"""
    
    # In production, fetch from database
    # For demo, return detailed mock data
    property_details = {
        'id': property_id,
        'basic_info': {
            'address': '789 Pine Road, Lake Mary, FL 32746',
            'price': 525000,
            'beds': 5,
            'baths': 3,
            'sqft': 3200,
            'price_per_sqft': 164,
            'lot_size': 0.35,
            'year_built': 2020,
            'property_type': 'Single Family',
            'days_on_market': 8,
            'mls_number': 'O6234567',
            'listing_agent': 'John Smith',
            'listing_office': 'ABC Realty'
        },
        'features': {
            'interior': [
                'Granite Countertops',
                'Stainless Steel Appliances',
                'Hardwood Floors',
                'Walk-in Closets',
                'Master Suite',
                'Office Space'
            ],
            'exterior': [
                'Pool',
                'Covered Patio',
                'Fenced Yard',
                'Sprinkler System',
                '3-Car Garage'
            ],
            'community': [
                'Gated Community',
                'HOA',
                'Tennis Courts',
                'Playground',
                'Walking Trails'
            ]
        },
        'financials': {
            'property_tax': 6300,
            'hoa_fee': 280,
            'insurance_estimate': 2400,
            'utilities_estimate': 250
        },
        'location': {
            'school_district': 'Seminole County',
            'elementary_school': 'Lake Mary Elementary (9/10)',
            'middle_school': 'Millennium Middle (8/10)',
            'high_school': 'Lake Mary High (9/10)',
            'walk_score': 72,
            'transit_score': 35,
            'bike_score': 65
        },
        'nearby_amenities': {
            'grocery_stores': [
                {'name': 'Publix', 'distance': 0.5},
                {'name': 'Whole Foods', 'distance': 1.2}
            ],
            'restaurants': 15,
            'parks': 3,
            'hospitals': [
                {'name': 'AdventHealth', 'distance': 2.3}
            ]
        }
    }
    
    return jsonify(property_details)

@comparison_bp.route('/api/compare', methods=['POST'])
@login_required
def compare_properties():
    """Compare multiple properties and generate scores"""
    data = request.get_json()
    property_ids = data.get('property_ids', [])
    
    if len(property_ids) < 2:
        return jsonify({'error': 'At least 2 properties required for comparison'}), 400
    
    if len(property_ids) > 4:
        return jsonify({'error': 'Maximum 4 properties can be compared'}), 400
    
    # In production, fetch actual property data and calculate real scores
    # For demo, return calculated comparison data
    
    comparison_data = {
        'properties': [],
        'scores': {
            'best_value': calculate_value_score(property_ids),
            'location': calculate_location_score(property_ids),
            'amenities': calculate_amenities_score(property_ids),
            'investment': calculate_investment_score(property_ids)
        },
        'recommendations': generate_recommendations(property_ids)
    }
    
    return jsonify(comparison_data)

@comparison_bp.route('/api/report/generate', methods=['POST'])
@login_required
def generate_comparison_report():
    """Generate a PDF comparison report"""
    data = request.get_json()
    property_ids = data.get('property_ids', [])
    
    # In production, generate actual PDF report
    report_data = {
        'success': True,
        'report_id': f'comp_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'download_url': f'/comparison/download/report_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf',
        'message': 'Comparison report generated successfully'
    }
    
    return jsonify(report_data)

@comparison_bp.route('/api/save', methods=['POST'])
@login_required
def save_comparison():
    """Save a comparison for later reference"""
    data = request.get_json()
    
    comparison = {
        'id': generate_comparison_id(),
        'name': data.get('name', 'Untitled Comparison'),
        'property_ids': data.get('property_ids', []),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat(),
        'user_id': current_user.id
    }
    
    # In production, save to database
    
    return jsonify({
        'success': True,
        'comparison_id': comparison['id'],
        'message': 'Comparison saved successfully'
    })

@comparison_bp.route('/api/saved')
@login_required
def get_saved_comparisons():
    """Get user's saved comparisons"""
    
    # In production, fetch from database
    saved_comparisons = [
        {
            'id': 'comp_001',
            'name': 'Smith Family Options',
            'property_count': 3,
            'created_at': '2024-06-10T14:30:00',
            'properties': ['123 Oak St', '456 Maple Ave', '789 Pine Rd']
        },
        {
            'id': 'comp_002',
            'name': 'Investment Properties',
            'property_count': 2,
            'created_at': '2024-06-08T10:15:00',
            'properties': ['321 Elm St', '555 Beach Blvd']
        }
    ]
    
    return jsonify(saved_comparisons)

# Helper functions
def calculate_value_score(property_ids):
    """Calculate value score based on price per sqft and features"""
    # Simplified calculation - expand in production
    base_score = 85
    # Adjust based on price per sqft, features, etc.
    return base_score

def calculate_location_score(property_ids):
    """Calculate location score based on schools, amenities, etc."""
    # Consider school ratings, walk score, nearby amenities
    return 92

def calculate_amenities_score(property_ids):
    """Calculate amenities score"""
    # Consider property features, community amenities
    return 78

def calculate_investment_score(property_ids):
    """Calculate investment potential score"""
    # Consider appreciation trends, rental potential, etc.
    return 88

def generate_recommendations(property_ids):
    """Generate AI-powered recommendations"""
    recommendations = [
        {
            'property_id': property_ids[0],
            'type': 'best_value',
            'reason': 'Lowest price per square foot with modern updates'
        },
        {
            'property_id': property_ids[1] if len(property_ids) > 1 else property_ids[0],
            'type': 'best_location',
            'reason': 'Highest-rated schools and walkable neighborhood'
        }
    ]
    
    return recommendations

def generate_comparison_id():
    """Generate unique comparison ID"""
    return f"comp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}"