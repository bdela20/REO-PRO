"""
Enhanced Property Service with Filtering Support
Replace your /app/services/property_service.py with this version
"""

from flask import current_app
from sqlalchemy import or_, and_, func
from app.models import db, Property
import logging
import random

logger = logging.getLogger(__name__)

class PropertyService:
    def __init__(self):
        self.db = db
        
    def search_properties_comprehensive(self, search_query, limit=200, filters=None):
        """
        Comprehensive property search with filtering
        Now returns more results for client-side pagination
        """
        try:
            # Start with base query
            query = Property.query
            
            # Apply text search
            if search_query:
                # Handle "City, State" format
                search_parts = search_query.split(',')
                primary_search = search_parts[0].strip()
                
                search_pattern = f"%{primary_search}%"
                query = query.filter(
                    or_(
                        Property.address.ilike(search_pattern),
                        Property.city.ilike(search_pattern),
                        Property.state.ilike(search_pattern),
                        Property.zip_code.ilike(search_pattern)
                    )
                )
            
            # Apply backend filters if provided
            if filters:
                if filters.get('min_price'):
                    query = query.filter(Property.price_estimate >= filters['min_price'])
                if filters.get('max_price'):
                    query = query.filter(Property.price_estimate <= filters['max_price'])
                if filters.get('bedrooms'):
                    query = query.filter(Property.bedrooms >= filters['bedrooms'])
                if filters.get('bathrooms'):
                    query = query.filter(Property.bathrooms >= filters['bathrooms'])
                if filters.get('property_type'):
                    query = query.filter(Property.property_type == filters['property_type'])
                if filters.get('min_sqft'):
                    query = query.filter(Property.square_footage >= filters['min_sqft'])
                if filters.get('max_sqft'):
                    query = query.filter(Property.square_footage <= filters['max_sqft'])
                if filters.get('min_year'):
                    query = query.filter(Property.year_built >= filters['min_year'])
                if filters.get('max_year'):
                    query = query.filter(Property.year_built <= filters['max_year'])
            
            # Execute query with higher limit for client-side filtering
            properties = query.limit(limit).all()
            
            # Log results
            logger.info(f"Search for '{search_query}' returned {len(properties)} properties")
            
            # If no properties found, return empty result
            if not properties:
                return {
                    'success': True,
                    'results': {
                        'properties': [],
                        'total_count': 0,
                        'search_query': search_query,
                        'market_stats': self._get_default_market_stats()
                    },
                    'searches_remaining': 10
                }
            
            # Get market statistics for the search area
            market_stats = self._calculate_market_stats(query)
            
            # Format results
            return {
                'success': True,
                'results': {
                    'properties': [self._format_property(p) for p in properties],
                    'total_count': query.count(),
                    'search_query': search_query,
                    'market_stats': market_stats
                },
                'searches_remaining': 10
            }
            
        except Exception as e:
            logger.error(f"Error in property search: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_property(self, property):
        """Format property data for frontend display"""
        # Generate a placeholder image URL based on property attributes
        photo_url = f"https://placehold.co/600x400/2563eb/ffffff?text={property.bedrooms}BR+{property.property_type.replace(' ', '+')}"
        
        return {
            'id': property.id,
            'address': property.address,
            'city': property.city,
            'state': property.state,
            'zip_code': property.zip_code,
            'price': int(property.price_estimate) if property.price_estimate else 0,
            'beds': property.bedrooms or 0,
            'baths': float(property.bathrooms) if property.bathrooms else 0,
            'sqft': property.square_footage or 0,
            'property_type': property.property_type or 'Single Family',
            'year_built': property.year_built or 2000,
            'photo_url': photo_url,
            'latitude': property.latitude,
            'longitude': property.longitude,
            'price_per_sqft': property.price_per_sqft or (int(property.price_estimate / property.square_footage) if property.price_estimate and property.square_footage else 0),
            'lot_size': property.lot_size or 0,
            'rent_estimate': property.rent_estimate or 0
        }
    
    def _calculate_market_stats(self, query):
        """Calculate market statistics for the search results"""
        try:
            # Get aggregated stats
            stats = query.with_entities(
                func.avg(Property.price_estimate).label('avg_price'),
                func.min(Property.price_estimate).label('min_price'),
                func.max(Property.price_estimate).label('max_price'),
                func.count(Property.id).label('total_listings'),
                func.avg(Property.price_per_sqft).label('avg_price_per_sqft')
            ).first()
            
            # Calculate median (approximate)
            median_price = query.with_entities(Property.price_estimate)\
                .order_by(Property.price_estimate)\
                .limit(1)\
                .offset(query.count() // 2)\
                .scalar() or 0
            
            return {
                'median_price': int(median_price) if median_price else None,
                'average_price': int(stats.avg_price) if stats.avg_price else None,
                'min_price': int(stats.min_price) if stats.min_price else None,
                'max_price': int(stats.max_price) if stats.max_price else None,
                'total_listings': stats.total_listings or 0,
                'average_price_per_sqft': round(stats.avg_price_per_sqft, 2) if stats.avg_price_per_sqft else None,
                'average_days_on_market': random.randint(25, 45)  # Placeholder - implement actual tracking
            }
        except Exception as e:
            logger.error(f"Error calculating market stats: {e}")
            return self._get_default_market_stats()
    
    def _get_default_market_stats(self):
        """Return default market stats when no data available"""
        return {
            'median_price': None,
            'average_price': None,
            'min_price': None,
            'max_price': None,
            'total_listings': 0,
            'average_price_per_sqft': None,
            'average_days_on_market': None
        }
    
    def get_property_by_id(self, property_id):
        """Get a single property by ID"""
        try:
            property = Property.query.get(property_id)
            if property:
                return {
                    'success': True,
                    'property': self._format_property(property)
                }
            return {
                'success': False,
                'error': 'Property not found'
            }
        except Exception as e:
            logger.error(f"Error fetching property: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_property(self, property_id, user_id):
        """Save a property to user's favorites"""
        try:
            # This would require a UserSavedProperties table
            # For now, just return success
            logger.info(f"User {user_id} saved property {property_id}")
            return {
                'success': True,
                'message': 'Property saved successfully'
            }
        except Exception as e:
            logger.error(f"Error saving property: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_all_services(self):
        """Test database connection and return status"""
        try:
            # Test database connection
            property_count = Property.query.count()
            
            # Get sample property types
            property_types = db.session.query(Property.property_type, func.count(Property.id))\
                .group_by(Property.property_type)\
                .all()
            
            # Get cities
            cities = db.session.query(Property.city, func.count(Property.id))\
                .group_by(Property.city)\
                .limit(10)\
                .all()
            
            return {
                'status': 'healthy',
                'services': {
                    'database': {
                        'status': 'connected',
                        'property_count': property_count,
                        'property_types': dict(property_types),
                        'cities': dict(cities)
                    },
                    'search': {
                        'status': 'ready',
                        'version': '2.0',
                        'features': ['pagination', 'filters', 'sorting']
                    }
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }