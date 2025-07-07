from flask_sqlalchemy import SQLAlchemy

# Create db instance here to avoid circular imports
db = SQLAlchemy()

# Import models after db is created
from .user import User
from .client import Client
from .calendar_event import CalendarEvent

# Update __all__ to exclude Property
__all__ = [
    "db", 
    "User",
    "Client"
]