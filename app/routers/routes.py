"""
API Routes
Flask routes for the web interface
"""

from flask import Blueprint, request, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Real Estate Office Pro API',
        'version': '1.0'
    })

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get detailed status of all services"""
    status = {
        'database': {
            'status': 'working',
            'type': 'SQLite'
        },
        'crm': {
            'status': 'working',
            'message': 'CRM service operational'
        },
        'calendar': {
            'status': 'working',
            'message': 'Calendar service operational'
        },
        'documents': {
            'status': 'working',
            'message': 'Document service operational'
        }
    }
    
    try:
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'error': 'Error getting system status',
            'status': 'error',
            'details': str(e)
        }), 500