"""
API Routes
Flask routes for the web interface
"""

from flask import Blueprint, request, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import services, but handle if they don't exist
try:
    from app.services import PropertyService
except ImportError:
    logger.warning("PropertyService not found - property search features will be disabled")
    PropertyService = None

# Create blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PropInsight API',
        'version': '1.0'
    })

@api_bp.route('/search', methods=['POST'])
def search_properties():
    """Search for properties with demographics"""
    try:
        # Check if PropertyService is available
        if PropertyService is None:
            return jsonify({
                'error': 'Property search service is not available',
                'status': 'error',
                'message': 'This feature is currently under development'
            }), 503
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing search query',
                'status': 'error'
            }), 400
        
        search_query = data.get('query', '').strip()
        limit = data.get('limit', 20)
        
        if not search_query:
            return jsonify({
                'error': 'Search query cannot be empty',
                'status': 'error'
            }), 400
        
        # Perform search
        property_service = PropertyService()
        results = property_service.search_properties_comprehensive(
            search_query=search_query,
            limit=min(limit, 100)  # Cap at 100 results
        )
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in property search: {e}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@api_bp.route('/test-services', methods=['GET'])
def test_services():
    """Test all API services"""
    try:
        if PropertyService is None:
            return jsonify({
                'status': 'partial',
                'message': 'Some services are not available',
                'services': {
                    'property_service': 'Not available',
                    'database': 'Connected'
                }
            })
        
        property_service = PropertyService()
        results = property_service.test_all_services()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error testing services: {e}")
        return jsonify({
            'error': 'Error testing services',
            'status': 'error'
        }), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get detailed status of all services"""
    status = {
        'database': {
            'status': 'working',
            'type': 'SQLite'
        }
    }
    
    try:
        # Try to import and check RentCast service
        try:
            from app.services.rentcast_service import RentCastService
            rentcast = RentCastService()
            status['rentcast'] = rentcast.get_api_status()
        except ImportError:
            status['rentcast'] = {'status': 'not configured', 'message': 'RentCast service not available'}
        
        # Try to import and check Census service
        try:
            from app.services.census_service import CensusService
            census = CensusService()
            status['census'] = census.get_api_status()
        except ImportError:
            status['census'] = {'status': 'not configured', 'message': 'Census service not available'}
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'error': 'Error getting system status',
            'status': 'error',
            'details': str(e)
        }), 500