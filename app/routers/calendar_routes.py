"""
Calendar Routes
API endpoints for calendar functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.calendar_event import CalendarEvent
from app.models.client import Client  # ← Keep only this import
from datetime import datetime, timedelta
from functools import wraps

calendar_bp = Blueprint('calendar', __name__)


def api_login_required(f):
    """Login required decorator that returns JSON for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'redirect': '/auth/login'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@calendar_bp.route('/api/calendar/events', methods=['GET'])
@api_login_required
def get_events():
    """Get all events for the current user with optional date filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        event_type = request.args.get('type')
        client_id = request.args.get('client_id')
        
        # Base query
        query = CalendarEvent.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(CalendarEvent.start_datetime >= start)
            
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(CalendarEvent.start_datetime <= end)
            
        if event_type:
            query = query.filter_by(type=event_type)
            
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        # Get events
        events = query.order_by(CalendarEvent.start_datetime).all()
        
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch events'
        }), 500


@calendar_bp.route('/api/calendar/events', methods=['POST'])
@api_login_required
def create_event():
    """Create a new calendar event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('date') or not data.get('time'):
            return jsonify({
                'success': False,
                'error': 'Title, date, and time are required'
            }), 400
        
        # Parse date and time more carefully
        date_string = data['date']
        
        # If date already includes time (T separator), parse it directly
        if 'T' in date_string:
            # Remove any timezone indicators to treat as local time
            date_string = date_string.split('+')[0].split('Z')[0]
            event_date = datetime.fromisoformat(date_string)
        else:
            # Otherwise combine date and time
            time_string = data['time']
            combined_string = f"{date_string}T{time_string}:00"
            event_date = datetime.fromisoformat(combined_string)
        
        # Handle property field for showings
        location = None
        if data.get('type') == 'showing' and data.get('property'):
            location = data.get('property')
        else:
            location = data.get('location')
        
        # Create new event
        event = CalendarEvent(
            user_id=current_user.id,
            title=data.get('title'),
            type=data.get('type', 'meeting'),
            start_datetime=event_date,  # This is now in local time
            duration=int(data.get('duration', 60)),
            all_day=data.get('duration') == 'all-day',
            client_id=data.get('client_id') if data.get('client_id') else None,
            property_id=None,  # Will be used when property management is implemented
            location=location,
            notes=data.get('notes'),
            reminder=int(data.get('reminder', 15)) if data.get('reminder') != 'none' else -1
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Handle Google Calendar sync if requested
        sync_to_google = data.get('sync_to_google', False)
        if sync_to_google:
            try:
                # Import here to avoid circular imports
                from app.google_calendar import sync_single_event_to_google_internal
                
                print(f"Attempting to sync event {event.id} to Google Calendar...")
                sync_result = sync_single_event_to_google_internal(event.id, current_user.id)
                
                if sync_result['success']:
                    print(f"Successfully synced to Google Calendar with ID: {sync_result.get('google_event_id')}")
                else:
                    print(f"Failed to sync to Google Calendar: {sync_result.get('message')}")
                    # Don't fail the whole request, event is still saved locally
                    
            except ImportError as e:
                print(f"Google Calendar module not found: {e}")
                # Continue anyway - event is saved locally
            except Exception as e:
                print(f"Error syncing to Google Calendar: {e}")
                # Continue anyway - event is saved locally
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': event.to_dict(),
            'event_id': event.id  # Make sure to include event_id for frontend
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating event: {str(e)}")
        print(f"Received data: {data}")  # Debug log
        return jsonify({
            'success': False,
            'error': f'Failed to create event: {str(e)}'
        }), 500


@calendar_bp.route('/api/calendar/events/<string:event_id>', methods=['PUT'])
@api_login_required
def update_event(event_id):
    """Update an existing calendar event"""
    try:
        # Find the event and ensure it belongs to the current user
        event = CalendarEvent.query.filter_by(
            id=event_id,
            user_id=current_user.id
        ).first()
        
        if not event:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            event.title = data['title']
            
        if 'type' in data:
            event.type = data['type']
            
        if 'date' in data:
            date_string = data['date']
            
            # Handle date with time
            if 'T' in date_string:
                date_string = date_string.split('+')[0].split('Z')[0]
                event.start_datetime = datetime.fromisoformat(date_string)
            elif 'time' in data:
                # Combine date and time
                time_string = data['time']
                combined_string = f"{date_string}T{time_string}:00"
                event.start_datetime = datetime.fromisoformat(combined_string)
            
        if 'duration' in data:
            event.duration = int(data['duration']) if data['duration'] != 'all-day' else 1440
            event.all_day = data['duration'] == 'all-day'
            
        if 'client_id' in data:
            event.client_id = data['client_id'] if data['client_id'] else None
            
        # Handle property/location based on event type
        if data.get('type') == 'showing' and 'property' in data and data['property']:
            event.location = data['property']
            event.property_id = None
        elif 'location' in data:
            event.location = data['location']
            
        if 'notes' in data:
            event.notes = data['notes']
            
        if 'reminder' in data:
            event.reminder = int(data['reminder']) if data['reminder'] != 'none' else -1
            
        if 'status' in data:
            event.status = data['status']
            
        if 'completed' in data:
            event.completed = data['completed']
        
        # Update timestamp
        event.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Handle Google Calendar sync if requested
        sync_to_google = data.get('sync_to_google', False)
        if sync_to_google and hasattr(event, 'google_event_id') and not event.google_event_id:
            try:
                from app.google_calendar import sync_single_event_to_google_internal
                sync_result = sync_single_event_to_google_internal(event.id, current_user.id)
                if not sync_result['success']:
                    print(f"Failed to sync updated event to Google: {sync_result.get('message')}")
            except Exception as e:
                print(f"Error syncing updated event to Google: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Event updated successfully',
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating event: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update event: {str(e)}'
        }), 500


@calendar_bp.route('/api/calendar/events/<string:event_id>', methods=['DELETE'])
@api_login_required
def delete_event(event_id):
    """Delete a calendar event"""
    try:
        # Find the event and ensure it belongs to the current user
        event = CalendarEvent.query.filter_by(
            id=event_id,
            user_id=current_user.id
        ).first()
        
        if not event:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # If event was synced to Google, we might want to delete it there too
        # For now, we'll just delete locally
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting event: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete event'
        }), 500


@calendar_bp.route('/api/calendar/events/<string:event_id>', methods=['GET'])
@api_login_required
def get_event(event_id):
    """Get a specific event"""
    try:
        event = CalendarEvent.query.filter_by(
            id=event_id,
            user_id=current_user.id
        ).first()
        
        if not event:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        return jsonify({
            'success': True,
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error fetching event: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch event'
        }), 500


@calendar_bp.route('/api/calendar/events/upcoming', methods=['GET'])
@api_login_required
def get_upcoming_events():
    """Get upcoming events for the dashboard"""
    try:
        # Get limit from query params (default 5)
        limit = int(request.args.get('limit', 5))
        
        # Get events starting from now
        now = datetime.utcnow()
        
        events = CalendarEvent.query.filter_by(
            user_id=current_user.id
        ).filter(
            CalendarEvent.start_datetime >= now,
            CalendarEvent.status != 'cancelled'
        ).order_by(
            CalendarEvent.start_datetime
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        print(f"Error fetching upcoming events: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch upcoming events'
        }), 500


@calendar_bp.route('/api/calendar/stats', methods=['GET'])
@api_login_required
def get_calendar_stats():
    """Get calendar statistics for the dashboard"""
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Calculate week range (Monday to Sunday)
        days_since_monday = now.weekday()
        week_start = today_start - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=7)
        
        # Calculate month range
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all user's events for the month (more efficient than multiple queries)
        month_events = CalendarEvent.query.filter(
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.status != 'cancelled',
            CalendarEvent.start_datetime >= month_start,
            CalendarEvent.start_datetime < month_end
        ).all()
        
        # Calculate counts
        today_count = sum(1 for e in month_events 
                         if today_start <= e.start_datetime < today_end)
        
        week_count = sum(1 for e in month_events 
                        if week_start <= e.start_datetime < week_end)
        
        month_count = len(month_events)
        
        # Get upcoming events in next 24 hours
        tomorrow = now + timedelta(days=1)
        upcoming_24h = sum(1 for e in month_events 
                          if now <= e.start_datetime < tomorrow)
        
        # Get breakdown by type for today
        breakdown = {
            'showing': sum(1 for e in month_events if e.type == 'showing' and today_start <= e.start_datetime < today_end),
            'meeting': sum(1 for e in month_events if e.type == 'meeting' and today_start <= e.start_datetime < today_end),
            'task': sum(1 for e in month_events if e.type == 'task' and today_start <= e.start_datetime < today_end),
            'reminder': sum(1 for e in month_events if e.type == 'reminder' and today_start <= e.start_datetime < today_end)
        }
        
        # Get next event
        next_event = CalendarEvent.query.filter(
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.status != 'cancelled',
            CalendarEvent.start_datetime >= now
        ).order_by(CalendarEvent.start_datetime).first()
        
        stats = {
            # Keep camelCase for backward compatibility
            'todayEvents': today_count,
            'weekEvents': week_count,
            'monthEvents': month_count,  # Added this
            
            # Also include snake_case versions
            'today_events': today_count,
            'week_events': week_count,
            'month_events': month_count,
            'upcoming_24h': upcoming_24h,
            'breakdown': breakdown,
            
            # Keep existing fields
            'upcomingShowings': sum(1 for e in month_events if e.type == 'showing' and e.start_datetime >= now),
            'tasksDue': sum(1 for e in month_events if e.type == 'task' and not e.completed),
            'nextEvent': next_event.to_dict() if next_event else None
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Error fetching calendar stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch calendar stats',
            'stats': {
                'today_events': 0,
                'week_events': 0,
                'month_events': 0,
                'todayEvents': 0,
                'weekEvents': 0,
                'monthEvents': 0
            }
        }), 500


@calendar_bp.route('/api/calendar/clients', methods=['GET'])
@api_login_required
def get_clients():
    try:
        # Debug prints
        print(f"Current user ID: {current_user.id}, Type: {type(current_user.id)}")
        print(f"Current user object: {current_user}")
        
        # Get all clients for the current user
        clients = Client.query.filter_by(
            user_id=current_user.id
        ).order_by(Client.first_name, Client.last_name).all()
        
        print(f"Found {len(clients)} clients")
        
        # If no clients found, let's check if there are ANY clients in the database
        if len(clients) == 0:
            all_clients = Client.query.all()
            print(f"Total clients in database: {len(all_clients)}")
            if len(all_clients) > 0:
                print(f"First client user_id: {all_clients[0].user_id}, type: {type(all_clients[0].user_id)}")
        
        # Format for the dropdown
        client_list = []
        for client in clients:
            # Debug first client
            if len(client_list) == 0:
                print(f"First client: {client.first_name} {client.last_name}, ID: {client.id}")
            
            client_list.append({
                'id': client.id,
                'name': f"{client.first_name} {client.last_name}",
                'email': client.email,
                'phone': client.phone,
                'type': client.type,
                'category': client.category
            })
        
        response_data = {
            'success': True,
            'clients': client_list
        }
        
        print(f"Sending response: {response_data}")
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Error fetching clients: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch clients'
        }), 500


# Add the sync endpoint for single events
@calendar_bp.route('/api/calendar/events/<string:event_id>/sync-to-google', methods=['POST'])
@api_login_required
def sync_event_to_google(event_id):
    """Sync a single event to Google Calendar"""
    try:
        from app.google_calendar import sync_single_event_to_google_internal
        
        result = sync_single_event_to_google_internal(event_id, current_user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Event synced to Google Calendar',
                'google_event_id': result.get('google_event_id')
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to sync event')
            }), 400
            
    except ImportError:
        return jsonify({
            'success': False,
            'message': 'Google Calendar integration not configured'
        }), 501
    except Exception as e:
        print(f"Error syncing event to Google: {e}")
        return jsonify({
            'success': False,
            'message': f'Error syncing event: {str(e)}'
        }), 500