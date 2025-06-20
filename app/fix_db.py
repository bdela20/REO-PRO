from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if it worked
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n✅ Database tables:")
    for table in tables:
        print(f"   - {table}")
    
    if 'clients' in tables:
        print("\n✅ SUCCESS! Clients table exists!")
    else:
        print("\n❌ ERROR: Clients table was NOT created!")