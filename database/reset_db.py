import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

from app import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Database tables recreated successfully")
    
    from app.models import Property
    count = Property.query.count()
    print(f"✅ Database test passed - {count} properties found")
