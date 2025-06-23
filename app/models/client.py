from app.models import db
from datetime import datetime
import uuid


class Client(db.Model):
    __tablename__ = 'clients'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    
    # Client Status
    type = db.Column(db.String(20), default='lead')  # lead, active, past
    category = db.Column(db.String(20), default='buyer')  # buyer, seller, both
    
    # Property Preferences
    budget_min = db.Column(db.Integer)
    budget_max = db.Column(db.Integer)
    location = db.Column(db.String(200))
    property_type = db.Column(db.String(50))  # single-family, condo, townhouse
    min_beds = db.Column(db.Integer)
    min_baths = db.Column(db.Float)
    
    # Lead Information
    source = db.Column(db.String(50))  # website, referral, social, other
    timeline = db.Column(db.String(50))  # asap, 1-3months, 3-6months, 6months+
    notes = db.Column(db.Text)
    
    # Tracking
    last_contact = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('clients', lazy='dynamic'))
    
    def to_dict(self):
        """Convert client to dictionary for JSON response"""
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'type': self.type,
            'category': self.category,
            'budgetMin': self.budget_min,
            'budgetMax': self.budget_max,
            'location': self.location,
            'propertyType': self.property_type,
            'minBeds': self.min_beds,
            'minBaths': self.min_baths,
            'source': self.source,
            'timeline': self.timeline,
            'notes': self.notes,
            'lastContact': self.last_contact.isoformat() if self.last_contact else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Client {self.first_name} {self.last_name}>'