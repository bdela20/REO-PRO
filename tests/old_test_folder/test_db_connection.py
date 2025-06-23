import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        # Connect using the DATABASE_URL from .env
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to: {version[0]}")
        
        # Check our tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"📊 Tables created: {[table[0] for table in tables]}")
        
        # Test sample data
        cursor.execute("SELECT COUNT(*) FROM properties;")
        count = cursor.fetchone()[0]
        print(f"🏠 Properties in database: {count}")
        
        # Test inserting a record
        cursor.execute("""
            INSERT INTO properties (address, city, state, estimated_value) 
            VALUES ('Test Address', 'Test City', 'TX', 100000.00)
            ON CONFLICT (address, city, state) DO NOTHING;
        """)
        conn.commit()
        
        # Check count again
        cursor.execute("SELECT COUNT(*) FROM properties;")
        new_count = cursor.fetchone()[0]
        print(f"🏠 Properties after test insert: {new_count}")
        
        conn.close()
        print("🎉 Database setup successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your .env file has the correct DATABASE_URL")

if __name__ == "__main__":
    print("🧪 Testing PropInsight Database Connection")
    print("=" * 45)
    test_connection()