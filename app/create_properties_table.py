"""
Create Properties Table
Run this to create the properties table
"""

from app import create_app
from app.models import db

def create_tables():
    app = create_app()
    
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()