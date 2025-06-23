import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    
    # Connect to database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    
    print("✅ Database connection successful!")
    print(f"PostgreSQL version: {result[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")