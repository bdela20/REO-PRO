from datetime import datetime
from . import db

class Property(db.Model):
    __tablename__ = "properties"
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Property details
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    square_footage = db.Column(db.Integer)
    lot_size = db.Column(db.Float)
    year_built = db.Column(db.Integer)
    property_type = db.Column(db.String(50))
    
    # Financial data
    rent_estimate = db.Column(db.Float)
    price_estimate = db.Column(db.Float)
    price_per_sqft = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "square_footage": self.square_footage,
            "rent_estimate": self.rent_estimate,
            "price_estimate": self.price_estimate,
            "source": self.source
        }