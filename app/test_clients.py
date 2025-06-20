from app import create_app
from app.models import db, User, Client
from flask import jsonify

app = create_app()

with app.app_context():
    # Check if tables exist
    print("\n📊 Database Tables:")
    print(db.engine.table_names())
    
    # Check if Client model is loaded
    print(f"\n✅ Client model loaded: {Client is not None}")
    
    # Test creating a client (if you have a test user)
    test_user = User.query.first()
    if test_user:
        print(f"\n👤 Test user: {test_user.email}")
        
        # Check existing clients
        client_count = Client.query.filter_by(user_id=test_user.id).count()
        print(f"📋 Existing clients: {client_count}")
    else:
        print("\n⚠️ No users found - create a user first")

print("\n✅ Test complete!")