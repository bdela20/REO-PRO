#!/usr/bin/env python3
"""Create Google Calendar tables in the database"""

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

print("🔧 Creating Google Calendar tables...")

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

# Check if calendar_events table has google sync columns
cursor.execute("PRAGMA table_info(calendar_events)")
columns = [col[1] for col in cursor.fetchall()]

# Add google_event_id column if missing
if 'google_event_id' not in columns:
    try:
        cursor.execute("""
        ALTER TABLE calendar_events 
        ADD COLUMN google_event_id TEXT
        """)
        print("✅ Added google_event_id column to calendar_events")
    except Exception as e:
        print(f"❌ Error adding google_event_id column: {e}")

# Add last_synced column if missing
if 'last_synced' not in columns:
    try:
        cursor.execute("""
        ALTER TABLE calendar_events 
        ADD COLUMN last_synced TIMESTAMP
        """)
        print("✅ Added last_synced column to calendar_events")
    except Exception as e:
        print(f"❌ Error adding last_synced column: {e}")

# Check if users table exists and has last_google_sync column
try:
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in cursor.fetchall()]
    
    if 'last_google_sync' not in user_columns:
        cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN last_google_sync TIMESTAMP
        """)
        print("✅ Added last_google_sync column to users table")
except Exception as e:
    print(f"⚠️  Could not add last_google_sync to users table: {e}")

# Commit changes
conn.commit()

# Verify tables
print("\n📊 Verifying database structure...")

# Check google_calendar_tokens
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='google_calendar_tokens'")
result = cursor.fetchone()
if result:
    print("\n✅ google_calendar_tokens table structure:")
    print(result[0])
else:
    print("\n❌ google_calendar_tokens table not found!")

# Check calendar_events columns
cursor.execute("PRAGMA table_info(calendar_events)")
columns = cursor.fetchall()
print("\n📋 calendar_events columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

print("\n✨ Database setup complete!")
print("\nNext steps:")
print("1. Restart your Flask application")
print("2. Try creating an event with Google Calendar sync")
print("3. If you haven't connected Google Calendar yet, click 'Add to Google' on an event")