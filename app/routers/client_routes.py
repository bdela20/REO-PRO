from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.client import Client
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, session
from flask_login import login_required
from app.models import Client, db

client_bp = Blueprint('client', __name__)


def api_login_required(f):
    """Login required decorator that returns JSON for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'redirect': '/auth/login'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@client_bp.route('/api/clients', methods=['GET'])
@api_login_required
def get_clients():
    """Get all clients for the current user"""
    try:
        # Get all clients belonging to the current user
        clients = Client.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'success': True,
            'clients': [client.to_dict() for client in clients]
        }), 200
        
    except Exception as e:
        print(f"Error fetching clients: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch clients'
        }), 500


@client_bp.route('/api/clients', methods=['POST'])
@api_login_required
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('firstName') or not data.get('lastName') or not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'First name, last name, and email are required'
            }), 400
        
        # Check if client with this email already exists for this user
        existing_client = Client.query.filter_by(
            user_id=current_user.id,
            email=data.get('email')
        ).first()
        
        if existing_client:
            return jsonify({
                'success': False,
                'error': 'A client with this email already exists'
            }), 400
        
        # Create new client
        client = Client(
            user_id=current_user.id,
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            type=data.get('type', 'lead'),
            category=data.get('category', 'buyer'),
            budget_min=data.get('budgetMin'),
            budget_max=data.get('budgetMax'),
            location=data.get('location'),
            property_type=data.get('propertyType'),
            min_beds=data.get('minBeds'),
            min_baths=data.get('minBaths'),
            source=data.get('source'),
            timeline=data.get('timeline'),
            notes=data.get('notes')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Client created successfully',
            'client': client.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating client: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create client'
        }), 500


@client_bp.route('/api/clients/<string:client_id>', methods=['PUT'])
@api_login_required
def update_client(client_id):
    """Update an existing client"""
    try:
        # Find the client and ensure it belongs to the current user
        client = Client.query.filter_by(
            id=client_id,
            user_id=current_user.id
        ).first()
        
        if not client:
            return jsonify({
                'success': False,
                'error': 'Client not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'firstName' in data:
            client.first_name = data['firstName']
        if 'lastName' in data:
            client.last_name = data['lastName']
        if 'email' in data:
            # Check if new email already exists for another client
            existing_client = Client.query.filter_by(
                user_id=current_user.id,
                email=data['email']
            ).filter(Client.id != client_id).first()
            
            if existing_client:
                return jsonify({
                    'success': False,
                    'error': 'Another client with this email already exists'
                }), 400
                
            client.email = data['email']
        
        # Update other fields
        if 'phone' in data:
            client.phone = data['phone']
        if 'type' in data:
            client.type = data['type']
        if 'category' in data:
            client.category = data['category']
        if 'budgetMin' in data:
            client.budget_min = data['budgetMin']
        if 'budgetMax' in data:
            client.budget_max = data['budgetMax']
        if 'location' in data:
            client.location = data['location']
        if 'propertyType' in data:
            client.property_type = data['propertyType']
        if 'minBeds' in data:
            client.min_beds = data['minBeds']
        if 'minBaths' in data:
            client.min_baths = data['minBaths']
        if 'source' in data:
            client.source = data['source']
        if 'timeline' in data:
            client.timeline = data['timeline']
        if 'notes' in data:
            client.notes = data['notes']
        
        # Update the updated_at timestamp
        client.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Client updated successfully',
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating client: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update client'
        }), 500


@client_bp.route('/api/clients/<string:client_id>', methods=['DELETE'])
@api_login_required
def delete_client(client_id):
    """Delete a client"""
    try:
        # Find the client and ensure it belongs to the current user
        client = Client.query.filter_by(
            id=client_id,
            user_id=current_user.id
        ).first()
        
        if not client:
            return jsonify({
                'success': False,
                'error': 'Client not found'
            }), 404
        
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Client deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting client: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete client'
        }), 500


@client_bp.route('/api/clients/<string:client_id>', methods=['GET'])
@api_login_required
def get_client(client_id):
    """Get a specific client"""
    try:
        client = Client.query.filter_by(
            id=client_id,
            user_id=current_user.id
        ).first()
        
        if not client:
            return jsonify({
                'success': False,
                'error': 'Client not found'
            }), 404
        
        return jsonify({
            'success': True,
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error fetching client: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch client'
        }), 500
        
@client_bp.route('/api/clients/stats', methods=['GET'])
@login_required
def get_client_stats():
    """Get client statistics for dashboard"""
    try:
        user_id = session.get('user_id')
        
        # Get all clients for the current user
        all_clients = Client.query.filter_by(user_id=user_id).all()
        
        # Get clients from 30 days ago for comparison
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Count new clients in last 30 days
        new_clients_count = len([c for c in all_clients if c.created_at and c.created_at > thirty_days_ago])
        
        # Calculate statistics with more meaningful metrics
        total_clients = len(all_clients)
        leads_count = len([c for c in all_clients if c.type == 'lead'])
        active_count = len([c for c in all_clients if c.type == 'active'])
        buyers_count = len([c for c in all_clients if c.category in ['buyer', 'both']])
        
        # Calculate percentage change
        if total_clients > 0:
            # If we have new clients in the last 30 days, show growth
            if new_clients_count > 0:
                # Growth percentage based on new clients
                percentage_change = round((new_clients_count / max(total_clients - new_clients_count, 1)) * 100)
            else:
                percentage_change = 0
        else:
            percentage_change = 0
        
        # Hot leads: leads that need immediate attention (contacted > 7 days ago or never)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        hot_leads = len([c for c in all_clients if c.type == 'lead' and 
                        (not c.last_contact or c.last_contact < seven_days_ago)])
        
        stats = {
            'total_clients': total_clients,
            'active_leads': leads_count,  # All leads
            'qualified_buyers': active_count,  # Active clients (converted from leads)
            'hot_prospects': hot_leads,  # Leads needing follow-up
            'buyers_count': buyers_count,
            'sellers_count': len([c for c in all_clients if c.category in ['seller', 'both']]),
            'percentage_change': percentage_change,
            'new_clients_30d': new_clients_count
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500