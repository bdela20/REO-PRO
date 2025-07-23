#!/usr/bin/env python3
"""Setup Google Calendar database tables"""

import sqlite3
import os

# Database path
db_path = 'instance/propinsight.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔧 Setting up Google Calendar database tables...")

# Create google_calendar_tokens table
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS google_calendar_tokens (
        user_id INTEGER PRIMARY KEY,
        token TEXT NOT NULL,
        refresh_token TEXT,
        token_uri TEXT,
        client_id TEXT,
        client_secret TEXT,
        scopes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    print("✅ Created google_calendar_tokens table")
except Exception as e:
    print(f"❌ Error creating google_calendar_tokens table: {e}")

# Commit changes
conn.commit()

# Verify the table was created
print("\n📊 Verifying database structure...")

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"\n📋 All tables in database: {', '.join(tables)}")

# Check if google_calendar_tokens exists
if 'google_calendar_tokens' in tables:
    print("\n✅ google_calendar_tokens table verified!")
    
    # Show table structure
    cursor.execute("PRAGMA table_info(google_calendar_tokens)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\n❌ google_calendar_tokens table was not created!")

# Check if CalendarEvent has the necessary columns
print("\n📋 Checking calendar_events table...")
cursor.execute("PRAGMA table_info(calendar_events)")
columns = cursor.fetchall()
col_names = [col[1] for col in columns]

required_columns = ['google_event_id', 'last_synced']
missing_columns = [col for col in required_columns if col not in col_names]

if missing_columns:
    print(f"⚠️  Missing columns in calendar_events: {', '.join(missing_columns)}")
    print("   Run 'flask db migrate' and 'flask db upgrade' to add them")
else:
    print("✅ All required columns present in calendar_events")

conn.close()

print("\n✨ Database setup complete!")
print("\nNext steps:")
print("1. Restart your Flask application")
print("2. Try creating an event with 'Add to Google Calendar' checked")
print("3. Check the Flask logs for any errors")