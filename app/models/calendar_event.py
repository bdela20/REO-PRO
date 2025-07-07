"""
Calendar Event Model
Database model for calendar events
"""

from app.models import db
from datetime import datetime
import uuid

class CalendarEvent(db.Model):
    """Calendar event model for storing appointments, showings, meetings, etc."""
    
    __tablename__ = 'calendar_events'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Event basic info
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # showing, meeting, task, reminder
    
    # Date and time
    start_datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=60)  # duration in minutes
    all_day = db.Column(db.Boolean, default=False)
    
    # Related entities
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    property_id = db.Column(db.String(36), nullable=True)  # For future property model
    
    # Event details
    location = db.Column(db.String(300))
    notes = db.Column(db.Text)
    reminder = db.Column(db.Integer, default=15)  # reminder in minutes before event, -1 for none
    
    # Google Calendar sync
    google_event_id = db.Column(db.String(100), unique=True, nullable=True)
    google_calendar_id = db.Column(db.String(100), nullable=True)
    google_sync_token = db.Column(db.String(100), nullable=True)
    last_synced = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='confirmed')  # confirmed, tentative, cancelled
    completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('calendar_events', lazy='dynamic'))
    client = db.relationship('Client', backref=db.backref('calendar_events', lazy='dynamic'))
    
    def to_dict(self):
        """Convert event to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'date': self.start_datetime.isoformat(),
            'startDateTime': self.start_datetime.isoformat(),
            'duration': self.duration,
            'allDay': self.all_day,
            'clientId': self.client_id,
            'clientName': self.client.first_name + ' ' + self.client.last_name if self.client else None,
            'propertyId': self.property_id,
            'location': self.location,
            'notes': self.notes,
            'reminder': self.reminder,
            'status': self.status,
            'completed': self.completed,
            'googleEventId': self.google_event_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CalendarEvent {self.title} on {self.start_datetime}>'