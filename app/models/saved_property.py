# 1. First, create a new model file: models/saved_property.py

from datetime import datetime
from . import db

class SavedProperty(db.Model):
    """Many-to-many relationship between users and properties"""
    __tablename__ = 'saved_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Optional notes about the property
    
    # Create unique constraint to prevent duplicate saves
    __table_args__ = (
        db.UniqueConstraint('user_id', 'property_id', name='unique_user_property'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('saved_properties', lazy='dynamic'))
    property = db.relationship('Property', backref=db.backref('saved_by_users', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None,
            'notes': self.notes
        }


# 2. Update your models/__init__.py to include SavedProperty
# Add this import: from .saved_property import SavedProperty


# 3. Add these relationships to your existing models:
# In user.py, add:
# saved_properties_list = db.relationship('SavedProperty', back_populates='user', lazy='dynamic')

# In property.py, add:
# saved_by = db.relationship('SavedProperty', back_populates='property', lazy='dynamic')


# 4. Create a new file: routes/property_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Property, SavedProperty, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
import logging

logger = logging.getLogger(__name__)

property_bp = Blueprint('properties', __name__, url_prefix='/api/properties')

@property_bp.route('/search', methods=['POST'])
@login_required
def search_properties():
    """Search properties with saved status for current user"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        # Filters
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        min_beds = data.get('min_beds')
        min_baths = data.get('min_baths')
        property_type = data.get('property_type')
        
        # Build query
        properties_query = Property.query
        
        if query:
            search_filter = or_(
                Property.address.ilike(f'%{query}%'),
                Property.city.ilike(f'%{query}%'),
                Property.state.ilike(f'%{query}%'),
                Property.zip_code.ilike(f'%{query}%')
            )
            properties_query = properties_query.filter(search_filter)
        
        if min_price:
            properties_query = properties_query.filter(Property.price_estimate >= min_price)
        if max_price:
            properties_query = properties_query.filter(Property.price_estimate <= max_price)
        if min_beds:
            properties_query = properties_query.filter(Property.bedrooms >= min_beds)
        if min_baths:
            properties_query = properties_query.filter(Property.bathrooms >= min_baths)
        if property_type:
            properties_query = properties_query.filter(Property.property_type == property_type)
        
        # Execute query
        properties = properties_query.limit(50).all()
        
        # Get saved property IDs for current user
        saved_property_ids = set()
        if current_user.is_authenticated:
            saved_property_ids = set(
                sp.property_id for sp in SavedProperty.query.filter_by(user_id=current_user.id).all()
            )
        
        # Format results
        results = []
        for prop in properties:
            prop_dict = prop.to_dict()
            prop_dict['is_saved'] = prop.id in saved_property_ids
            results.append(prop_dict)
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'properties': results
        })
        
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to search properties'
        }), 500


@property_bp.route('/<int:property_id>/save', methods=['POST'])
@login_required
def save_property(property_id):
    """Save a property for the current user"""
    try:
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return jsonify({
                'status': 'error',
                'message': 'Property not found'
            }), 404
        
        # Check if already saved
        existing = SavedProperty.query.filter_by(
            user_id=current_user.id,
            property_id=property_id
        ).first()
        
        if existing:
            return jsonify({
                'status': 'success',
                'message': 'Property already saved'
            })
        
        # Save the property
        saved_property = SavedProperty(
            user_id=current_user.id,
            property_id=property_id,
            notes=request.json.get('notes', '')
        )
        
        db.session.add(saved_property)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Property saved successfully',
            'saved_property': saved_property.to_dict()
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Property already saved'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving property: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to save property'
        }), 500


@property_bp.route('/<int:property_id>/unsave', methods=['DELETE'])
@login_required
def unsave_property(property_id):
    """Remove a saved property for the current user"""
    try:
        saved_property = SavedProperty.query.filter_by(
            user_id=current_user.id,
            property_id=property_id
        ).first()
        
        if not saved_property:
            return jsonify({
                'status': 'error',
                'message': 'Property not in saved list'
            }), 404
        
        db.session.delete(saved_property)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Property removed from saved list'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unsaving property: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to remove property from saved list'
        }), 500


@property_bp.route('/saved', methods=['GET'])
@login_required
def get_saved_properties():
    """Get all saved properties for the current user"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get saved properties with pagination
        saved_query = SavedProperty.query.filter_by(user_id=current_user.id)\
            .order_by(SavedProperty.saved_at.desc())
        
        paginated = saved_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get full property details
        results = []
        for saved in paginated.items:
            prop_dict = saved.property.to_dict()
            prop_dict['is_saved'] = True
            prop_dict['saved_at'] = saved.saved_at.isoformat() if saved.saved_at else None
            prop_dict['notes'] = saved.notes
            results.append(prop_dict)
        
        return jsonify({
            'status': 'success',
            'properties': results,
            'total': paginated.total,
            'page': page,
            'pages': paginated.pages,
            'per_page': per_page
        })
        
    except Exception as e:
        logger.error(f"Error getting saved properties: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get saved properties'
        }), 500


@property_bp.route('/saved/count', methods=['GET'])
@login_required
def get_saved_count():
    """Get count of saved properties for the current user"""
    try:
        count = SavedProperty.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            'status': 'success',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Error getting saved count: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get saved count'
        }), 500


@property_bp.route('/saved/dashboard', methods=['GET'])
@login_required
def get_dashboard_saved_properties():
    """Get saved properties for dashboard display (limited to 5)"""
    try:
        saved_properties = SavedProperty.query.filter_by(user_id=current_user.id)\
            .order_by(SavedProperty.saved_at.desc())\
            .limit(5)\
            .all()
        
        results = []
        for saved in saved_properties:
            prop = saved.property
            results.append({
                'id': prop.id,
                'address': prop.address,
                'city': prop.city,
                'state': prop.state,
                'price': prop.price_estimate,
                'beds': prop.bedrooms,
                'baths': prop.bathrooms,
                'sqft': prop.square_footage,
                'saved_at': saved.saved_at.isoformat() if saved.saved_at else None,
                'photo_url': f'https://images.unsplash.com/photo-{prop.id % 10 + 1564013799919}?w=400'  # Placeholder
            })
        
        return jsonify({
            'status': 'success',
            'properties': results,
            'total_count': SavedProperty.query.filter_by(user_id=current_user.id).count()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard saved properties: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get dashboard properties'
        }), 500


# 5. Add this to your main app.py file to register the blueprint:
# from app.routes.property_routes import property_bp
# app.register_blueprint(property_bp)


# 6. Database migration command (run in terminal):
"""
flask db migrate -m "Add saved properties table"
flask db upgrade
"""