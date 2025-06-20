"""Add more properties to different cities"""
import random
from app import create_app
from app.models import db, Property

def add_more_properties():
    app = create_app()
    
    with app.app_context():
        # More Florida cities with properties
        cities_to_add = [
            {'city': 'Miami', 'state': 'FL', 'zip': '33101', 'count': 15},
            {'city': 'Tampa', 'state': 'FL', 'zip': '33602', 'count': 10},
            {'city': 'Jacksonville', 'state': 'FL', 'zip': '32099', 'count': 8},
            {'city': 'Fort Lauderdale', 'state': 'FL', 'zip': '33301', 'count': 7},
            {'city': 'West Palm Beach', 'state': 'FL', 'zip': '33401', 'count': 5},
        ]
        
        streets = ['Ocean', 'Beach', 'Sunset', 'Palm', 'Bay', 'Harbor', 'Marina']
        types = ['Ave', 'Blvd', 'Way', 'Dr', 'St']
        
        for city_info in cities_to_add:
            print(f"Adding {city_info['count']} properties to {city_info['city']}...")
            
            for i in range(city_info['count']):
                property = Property(
                    address=f"{random.randint(100, 999)} {random.choice(streets)} {random.choice(types)}",
                    city=city_info['city'],
                    state=city_info['state'],
                    zip_code=city_info['zip'],
                    bedrooms=random.choice([2, 3, 4]),
                    bathrooms=random.choice([1.5, 2, 2.5, 3]),
                    square_footage=random.randint(1200, 3000),
                    price_estimate=random.randint(250000, 750000),
                    property_type=random.choice(['Single Family', 'Condo', 'Townhouse']),
                    year_built=random.randint(1995, 2023),
                    source='test_data'
                )
                db.session.add(property)
        
        db.session.commit()
        print("✅ Added more properties!")
        
        # Show summary
        total = Property.query.count()
        print(f"\n�� Total properties in database: {total}")
        
        cities = db.session.query(Property.city, db.func.count(Property.id))\
            .group_by(Property.city).all()
        
        print("\nProperties by city:")
        for city, count in cities:
            print(f"  - {city}: {count}")

if __name__ == "__main__":
    add_more_properties()
