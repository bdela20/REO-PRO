from flask_sqlalchemy import SQLAlchemy

# Create db instance here to avoid circular imports
db = SQLAlchemy()

# Import models after db is created
from .user import User
from .property import Property  # ADD THIS LINE!
from .client import Client

# Update __all__ to include Property
__all__ = [
    "db", 
    "User",
    "Property",  # ADD THIS!
    "Client"
]