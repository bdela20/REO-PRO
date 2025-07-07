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
    print(f"📋 Tables: {', '.join(tables)}")
    
    if 'calendar_events' in tables:
        print("\n✅ SUCCESS: calendar_events table EXISTS!")
        
        # Get column info
        columns = inspector.get_columns('calendar_events')
        print("\n📌 Table columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
            
        # Test creating an event
        try:
            from app.models.calendar_event import CalendarEvent
            from datetime import datetime
            
            # Get a user to test with
            from app.models import User
            test_user = User.query.first()
            
            if test_user:
                print(f"\n🧪 Testing with user: {test_user.email}")
                
                # Create a test event
                test_event = CalendarEvent(
                    user_id=test_user.id,
                    title="Test Calendar Event",
                    type="meeting",
                    start_datetime=datetime.utcnow(),
                    duration=60,
                    notes="This is a test event"
                )
                
                db.session.add(test_event)
                db.session.commit()
                
                print("✅ Test event created successfully!")
                
                # Count events
                event_count = CalendarEvent.query.count()
                print(f"📊 Total events in database: {event_count}")
                
                # Clean up test event
                db.session.delete(test_event)
                db.session.commit()
                print("🧹 Test event cleaned up")
            else:
                print("\n⚠️  No users found in database to test with")
                
        except Exception as e:
            print(f"\n❌ Error testing calendar: {e}")
            import traceback
            traceback.print_exc()
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
                print("\n🔍 Checking imports...")
                
                # Check if model is imported in __init__.py
                try:
                    from app.models import CalendarEvent as CE
                    print("✅ CalendarEvent is imported in models/__init__.py")
                except ImportError:
                    print("❌ CalendarEvent NOT imported in models/__init__.py")
                    print("   Add this line to app/models/__init__.py:")
                    print("   from .calendar_event import CalendarEvent")
                
        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("\n📁 Make sure these files exist:")
            print("   - app/models/calendar_event.py")
            print("   - app/routers/calendar_routes.py")
            print("\n📝 And that app/__init__.py has:")
            print("   from app.models.calendar_event import CalendarEvent")
            print("   from app.routers.calendar_routes import calendar_bp")
            print("   app.register_blueprint(calendar_bp)")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()