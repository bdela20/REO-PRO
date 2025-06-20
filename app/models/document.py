# app/models/document.py

from datetime import datetime
from app.models import db

class Document(db.Model):
    """Documents managed by users"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # purchase_agreement, listing_agreement, etc.
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    signed_file_path = db.Column(db.String(255))  # Path to signed version
    
    # Property association
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    property_address = db.Column(db.String(255))
    
    # Status and dates
    status = db.Column(db.String(20), default='draft')  # draft, sent, partially_signed, signed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='documents')
    
    def __repr__(self):
        return f'<Document {self.title}>'


class DocumentRecipient(db.Model):
    """Recipients for document signatures"""
    __tablename__ = 'document_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))  # signer, viewer, approver
    
    # Access and status
    access_token = db.Column(db.String(100), unique=True)  # Unique token for accessing document
    status = db.Column(db.String(20), default='pending')  # pending, viewed, signed, declined
    
    # Timestamps
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    viewed_at = db.Column(db.DateTime)
    signed_at = db.Column(db.DateTime)
    
    # Relationship
    document = db.relationship('Document', backref='recipients')
    
    def __repr__(self):
        return f'<DocumentRecipient {self.email} - {self.status}>'


class DocumentTemplate(db.Model):
    """Reusable document templates"""
    __tablename__ = 'document_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    # Template content and structure
    content = db.Column(db.Text)  # Template content
    fields = db.Column(db.JSON)  # Dynamic fields that need to be filled
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DocumentTemplate {self.name}>'