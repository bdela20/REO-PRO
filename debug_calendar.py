from app import create_app
from app.models import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if calendar_events table exists
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n" + "="*50)
    print("DATABASE DEBUG INFORMATION")
    print("="*50)
    
    print(f"\n📊 Total tables in database: {len(tables)}")
    print(f"�� Tables: {', '.join(tables)}")
    
    if 'calendar_events' in tables:
        print("\n✅ SUCCESS: calendar_events table EXISTS!")
        
        # Get column info
        columns = inspector.get_columns('calendar_events')
        print("\n📌 Table columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
    else:
        print("\n❌ ERROR: calendar_events table NOT FOUND!")
        print("\n🔧 Attempting to create table now...")
        
        # Try to import and create the model
        try:
            from app.models.calendar_event import CalendarEvent
            db.create_all()
            
            # Check again
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'calendar_events' in tables:
                print("✅ Table created successfully!")
            else:
                print("❌ Failed to create table!")
        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("\n📁 Make sure these files exist:")
            print("   - app/models/calendar_event.py")
            print("   - app/routers/calendar_routes.py")
