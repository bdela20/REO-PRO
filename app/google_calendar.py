# app/google_calendar.py

from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os
import json
import sqlite3

google_calendar_bp = Blueprint('google_calendar', __name__)

# Google OAuth2 settings
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_db():
    """Get database connection"""
    # Use propinsight.db in instance folder
    db_path = os.path.join(current_app.instance_path, 'propinsight.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db

def get_flow(state=None):
    """Create OAuth2 flow from client_secrets.json"""
    # Look for client_secrets.json in project root
    client_secrets_file = os.path.join(current_app.root_path, '..', 'client_secrets.json')
    
    if not os.path.exists(client_secrets_file):
        # Try current directory
        client_secrets_file = 'client_secrets.json'
    
    if os.path.exists(client_secrets_file):
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=SCOPES,
            state=state
        )
    else:
        # Fallback to environment variables
        client_config = {
            "web": {
                "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:5001/auth/google/callback"]
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            state=state
        )
    
    # Set redirect URI - using port 5001 to match your app
    flow.redirect_uri = url_for('google_calendar.google_callback', _external=True)
    return flow

@google_calendar_bp.route('/auth/google')
@login_required
def google_auth():
    """Initiate Google OAuth flow"""
    flow = get_flow()
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    session['state'] = state
    session['user_id'] = current_user.id
    return redirect(authorization_url)

@google_calendar_bp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    # Get state and user_id from session
    state = session.get('state')
    user_id = session.get('user_id')
    
    if not state or not user_id:
        return redirect('/calendar?error=Invalid session')
    
    try:
        flow = get_flow(state=state)
        
        # Get the authorization response
        flow.fetch_token(authorization_response=request.url)
        
        # Store credentials in database
        credentials = flow.credentials
        
        db = get_db()
        cursor = db.cursor()
        
        # Save or update credentials
        cursor.execute("""
            INSERT INTO google_calendar_tokens (user_id, token, refresh_token, token_uri, client_id, client_secret, scopes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                token = excluded.token,
                refresh_token = excluded.refresh_token,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id,
            credentials.token,
            credentials.refresh_token,
            credentials.token_uri,
            credentials.client_id,
            credentials.client_secret,
            json.dumps(list(credentials.scopes))
        ))
        
        db.commit()
        db.close()
        
        # Redirect back to calendar with success message
        return redirect('/calendar?connected=true')
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return redirect('/calendar?error=' + str(e))

@google_calendar_bp.route('/api/calendar/google/sync', methods=['POST'])
@login_required
def sync_google_calendar():
    """Sync events between REO-PRO and Google Calendar"""
    try:
        user_id = current_user.id
        db = get_db()
        cursor = db.cursor()
        
        # Get stored credentials
        creds_data = cursor.execute("""
            SELECT token, refresh_token, token_uri, client_id, client_secret, scopes
            FROM google_calendar_tokens
            WHERE user_id = ?
        """, (user_id,)).fetchone()
        
        if not creds_data:
            return jsonify({'success': False, 'message': 'Google Calendar not connected'}), 401
        
        # Create credentials object
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=json.loads(creds_data['scopes'])
        )
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update stored token
            cursor.execute("""
                UPDATE google_calendar_tokens
                SET token = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (creds.token, user_id))
            db.commit()
        
        # Build Google Calendar service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get sync direction from request
        sync_direction = request.json.get('direction', 'both')
        events_synced = 0
        
        if sync_direction in ['to_google', 'both']:
            # Sync REO-PRO events to Google Calendar
            events_synced += sync_to_google(user_id, service, db)
        
        if sync_direction in ['from_google', 'both']:
            # Sync Google Calendar events to REO-PRO
            events_synced += sync_from_google(user_id, service, db)
        
        db.close()
        
        # Update last sync time
        update_last_sync(user_id)
        
        return jsonify({
            'success': True, 
            'message': 'Calendar synced successfully',
            'events_synced': events_synced
        })
        
    except Exception as e:
        print(f"Sync error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def sync_to_google(user_id, service, db):
    """Sync REO-PRO events to Google Calendar"""
    cursor = db.cursor()
    events_synced = 0
    
    # Get all REO-PRO events
    events = cursor.execute("""
        SELECT e.*, c.name as client_name
        FROM calendar_events e
        LEFT JOIN clients c ON e.client_id = c.id
        WHERE e.user_id = ?
        ORDER BY e.date, e.time
    """, (user_id,)).fetchall()
    
    for event in events:
        # Parse date and time
        event_date = event['date']
        event_time = event['time'] or '09:00:00'
        start_datetime = f"{event_date}T{event_time}"
        
        # Calculate end time
        duration = event['duration'] or 60
        if duration == 'all-day':
            duration = 1440  # 24 hours
        else:
            duration = int(duration)
        
        # Convert to Google Calendar format
        google_event = {
            'summary': event['title'],
            'location': event['location'] or event['property'],
            'description': format_google_description(dict(event)),
            'start': {
                'dateTime': datetime.fromisoformat(start_datetime).isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': calculate_end_time(start_datetime, duration),
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': []
            }
        }
        
        # Add reminder if set
        reminder = event['reminder']
        if reminder and reminder != 'none' and reminder != -1:
            google_event['reminders']['overrides'].append({
                'method': 'popup',
                'minutes': int(reminder)
            })
        
        try:
            if event['google_event_id']:
                # Update existing Google event
                result = service.events().update(
                    calendarId='primary',
                    eventId=event['google_event_id'],
                    body=google_event
                ).execute()
            else:
                # Create new Google event
                result = service.events().insert(
                    calendarId='primary',
                    body=google_event
                ).execute()
                
                # Store Google event ID
                cursor.execute("""
                    UPDATE calendar_events
                    SET google_event_id = ?, last_synced = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (result['id'], event['id']))
                
            events_synced += 1
                
        except HttpError as e:
            print(f"Error syncing event {event['id']}: {e}")
    
    db.commit()
    return events_synced

def sync_from_google(user_id, service, db):
    """Sync Google Calendar events to REO-PRO"""
    cursor = db.cursor()
    events_synced = 0
    
    # Get events from the last 30 days to next 90 days
    now = datetime.utcnow()
    time_min = (now - timedelta(days=30)).isoformat() + 'Z'
    time_max = (now + timedelta(days=90)).isoformat() + 'Z'
    
    try:
        # Get Google Calendar events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        google_events = events_result.get('items', [])
        
        for g_event in google_events:
            # Skip if no start time or if it's an REO-PRO synced event
            if 'dateTime' not in g_event.get('start', {}):
                continue
            
            # Check if event already exists in REO-PRO
            existing = cursor.execute("""
                SELECT id FROM calendar_events
                WHERE user_id = ? AND google_event_id = ?
            """, (user_id, g_event['id'])).fetchone()
            
            if existing:
                continue  # Skip if already synced
            
            # Skip if this was originally from REO-PRO
            if '[Synced from REO-PRO]' in g_event.get('description', ''):
                continue
            
            # Parse event details
            start_dt = datetime.fromisoformat(g_event['start']['dateTime'].replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(g_event['end']['dateTime'].replace('Z', '+00:00'))
            duration = int((end_dt - start_dt).total_seconds() / 60)
            
            # Create new event in REO-PRO
            cursor.execute("""
                INSERT INTO calendar_events 
                (user_id, type, title, location, notes, date, time, duration, 
                 google_event_id, last_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_id,
                'meeting',  # Default type for Google events
                g_event.get('summary', 'Untitled Event'),
                g_event.get('location', ''),
                g_event.get('description', ''),
                start_dt.strftime('%Y-%m-%d'),
                start_dt.strftime('%H:%M:%S'),
                duration,
                g_event['id']
            ))
            
            events_synced += 1
        
        db.commit()
        
    except HttpError as e:
        print(f"Error fetching Google events: {e}")
    
    return events_synced

def format_google_description(event):
    """Format REO-PRO event description for Google Calendar"""
    description = f"Event Type: {event['type'].title()}\n"
    
    if event.get('client_name'):
        description += f"Client: {event['client_name']}\n"
    
    if event.get('property'):
        description += f"Property: {event['property']}\n"
    
    if event.get('notes'):
        description += f"\nNotes: {event['notes']}"
    
    description += f"\n\n[Synced from REO-PRO]"
    
    return description

def calculate_end_time(start_datetime, duration_minutes):
    """Calculate end time based on start time and duration"""
    start = datetime.fromisoformat(start_datetime)
    end = start + timedelta(minutes=int(duration_minutes))
    return end.isoformat()

def update_last_sync(user_id):
    """Update last sync timestamp for user"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'last_google_sync' in columns:
        cursor.execute("""
            UPDATE users SET last_google_sync = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        db.commit()
    
    db.close()

@google_calendar_bp.route('/api/calendar/google/status')
@login_required
def google_calendar_status():
    """Check if Google Calendar is connected"""
    user_id = current_user.id
    db = get_db()
    cursor = db.cursor()
    
    connected = cursor.execute("""
        SELECT 1 FROM google_calendar_tokens
        WHERE user_id = ?
    """, (user_id,)).fetchone()
    
    # Get last sync time
    last_sync = None
    try:
        user_data = cursor.execute("""
            SELECT last_google_sync FROM users WHERE id = ?
        """, (user_id,)).fetchone()
        
        if user_data and 'last_google_sync' in user_data.keys():
            last_sync = user_data['last_google_sync']
    except:
        pass  # Column might not exist yet
    
    db.close()
    
    return jsonify({
        'connected': connected is not None,
        'last_sync': last_sync
    })

@google_calendar_bp.route('/api/calendar/google/disconnect', methods=['POST'])
@login_required
def disconnect_google_calendar():
    """Disconnect Google Calendar"""
    user_id = current_user.id
    db = get_db()
    cursor = db.cursor()
    
    # Remove stored credentials
    cursor.execute("""
        DELETE FROM google_calendar_tokens
        WHERE user_id = ?
    """, (user_id,))
    
    # Remove Google event IDs from calendar events
    cursor.execute("""
        UPDATE calendar_events
        SET google_event_id = NULL, last_synced = NULL
        WHERE user_id = ?
    """, (user_id,))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Google Calendar disconnected'})
