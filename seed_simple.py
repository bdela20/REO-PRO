"""
Simple Property Seeder
Creates test properties for Florida
"""

import random
from app import create_app
from app.models import db, Property

def create_test_properties():
    """Create 50 test properties in Florida"""
    
    app = create_app()
    
    with app.app_context():
        # Check if we already have properties
        count = Property.query.count()
        if count > 0:
            print(f"Database already has {count} properties")
            return
        
        print("Creating test properties...")
        
        # Florida cities
        locations = [
            {'city': 'Orlando', 'state': 'FL', 'zip': '32801'},
            {'city': 'Miami', 'state': 'FL', 'zip': '33101'},
            {'city': 'Tampa', 'state': 'FL', 'zip': '33602'},
            {'city': 'Jacksonville', 'state': 'FL', 'zip': '32099'},
            {'city': 'Fort Lauderdale', 'state': 'FL', 'zip': '33301'},
        ]
        
        streets = ['Oak', 'Main', 'Park', 'Lake', 'Sunset']
        types = ['St', 'Ave', 'Blvd', 'Dr', 'Ln']
        
        # Create 50 properties
        for i in range(50):
            location = random.choice(locations)
            
            # Create property
            property = Property(
                address=f"{random.randint(100, 999)} {random.choice(streets)} {random.choice(types)}",
                city=location['city'],
                state=location['state'],
                zip_code=location['zip'],
                bedrooms=random.choice([2, 3, 3, 4, 4, 5]),
                bathrooms=random.choice([1, 1.5, 2, 2.5, 3]),
                square_footage=random.randint(1000, 3500),
                price_estimate=random.randint(200000, 800000),
                property_type=random.choice(['Single Family', 'Condo', 'Townhouse']),
                year_built=random.randint(1990, 2023),
                source='test_data'
            )
            
            db.session.add(property)
        
        # Save all
        db.session.commit()
        print("✅ Created 50 test properties!")

if __name__ == "__main__":
    create_test_properties()
