#!/usr/bin/env python3
"""
Script to update existing users to have unlimited searches
Run this once after updating the User model
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User

def update_users():
    """Update all existing users to have unlimited searches"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            print(f"Found {len(users)} users to update...")
            
            # Update each user
            for user in users:
                old_searches = user.searches_remaining
                user.searches_remaining = 999999
                print(f"Updated {user.username}: {old_searches} → 999999 searches")
            
            # Commit changes
            db.session.commit()
            print(f"\n✅ Successfully updated {len(users)} users!")
            print("All users now have unlimited searches.")
            
        except Exception as e:
            print(f"❌ Error updating users: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_users()