from app.models import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):  # Add UserMixin here
    # rest of your model...
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    
    # Profile fields
    full_name = db.Column(db.String(120))
    company = db.Column(db.String(120))
    role = db.Column(db.String(50), default='agent')  # agent, broker, investor, etc.
    
    # REMOVED phone, license_number, bio, profile_photo - they don't exist in database
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Subscription/Plan - UNLIMITED SEARCHES NOW
    plan = db.Column(db.String(20), default='free')  # free, basic, pro, enterprise
    searches_remaining = db.Column(db.Integer, default=999999)  # UNLIMITED FOR NOW
    searches_reset_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # OAuth fields (for Google login)
    google_id = db.Column(db.String(100), unique=True)
    oauth_provider = db.Column(db.String(50))
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def can_search(self):
        """Check if user can perform searches - UNLIMITED FOR NOW"""
        return True  # Always return True for unlimited searches
    
    def use_search(self):
        """Use one search - disabled for unlimited searches"""
        pass  # Do nothing for now - unlimited searches
    
    def reset_searches(self):
        """Reset search count - not needed for unlimited"""
        pass  # Do nothing for now
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'company': self.company,
            'role': self.role,
            'plan': self.plan,
            'searches_remaining': 999999,  # Show unlimited
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'