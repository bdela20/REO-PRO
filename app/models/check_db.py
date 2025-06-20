from app import create_app
from app.models import db, Client, User
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    # Check if tables exist
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("📊 Tables in database:")
    for table in tables:
        print(f"   - {table}")
    
    if 'clients' not in tables:
        print("\n❌ 'clients' table does not exist! Creating it now...")
        db.create_all()
        print("✅ Tables created!")
    else:
        print("\n✅ 'clients' table exists!")
        
        # Show columns
        columns = inspector.get_columns('clients')
        print("\n📋 Columns in 'clients' table:")
        for col in columns:
            print(f"   - {col['name']} ({col['type']})")
        
        # Count existing clients
        client_count = Client.query.count()
        print(f"\n📊 Total clients in database: {client_count}")
        
        # Show clients per user
        users = User.query.all()
        print("\n👥 Clients per user:")
        for user in users:
            user_clients = Client.query.filter_by(user_id=user.id).count()
            print(f"   - {user.email}: {user_clients} clients")