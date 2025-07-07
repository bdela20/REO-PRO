"""
Calendar Routes
API endpoints for calendar functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.calendar_event import CalendarEvent
from app.models.client import Client
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
        
        # Parse date and time
        event_date = datetime.fromisoformat(data['date'])
        time_parts = data['time'].split(':')
        event_date = event_date.replace(
            hour=int(time_parts[0]), 
            minute=int(time_parts[1])
        )
        
        # Create new event
        event = CalendarEvent(
            user_id=current_user.id,
            title=data.get('title'),
            type=data.get('type', 'meeting'),
            start_datetime=event_date,
            duration=int(data.get('duration', 60)),
            all_day=data.get('duration') == 'all-day',
            client_id=data.get('clientId') if data.get('clientId') else None,
            property_id=data.get('propertyId') if data.get('propertyId') else None,
            location=data.get('location'),
            notes=data.get('notes'),
            reminder=int(data.get('reminder', 15)) if data.get('reminder') != 'none' else -1
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating event: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create event'
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
            
        if 'date' in data and 'time' in data:
            event_date = datetime.fromisoformat(data['date'])
            time_parts = data['time'].split(':')
            event.start_datetime = event_date.replace(
                hour=int(time_parts[0]), 
                minute=int(time_parts[1])
            )
            
        if 'duration' in data:
            event.duration = int(data['duration']) if data['duration'] != 'all-day' else 1440
            event.all_day = data['duration'] == 'all-day'
            
        if 'clientId' in data:
            event.client_id = data['clientId'] if data['clientId'] else None
            
        if 'propertyId' in data:
            event.property_id = data['propertyId'] if data['propertyId'] else None
            
        if 'location' in data:
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
            'error': 'Failed to update event'
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
        week_end = today_start + timedelta(days=7)
        
        # Get all user's events
        all_events = CalendarEvent.query.filter_by(
            user_id=current_user.id,
            status='confirmed'
        ).all()
        
        # Today's events
        today_events = [e for e in all_events 
                       if today_start <= e.start_datetime < today_end]
        
        # This week's events
        week_events = [e for e in all_events 
                      if today_start <= e.start_datetime < week_end]
        
        # Upcoming showings
        upcoming_showings = [e for e in all_events 
                           if e.type == 'showing' and e.start_datetime >= now]
        
        # Tasks due this week
        tasks_due = [e for e in all_events 
                    if e.type == 'task' and 
                    today_start <= e.start_datetime < week_end and
                    not e.completed]
        
        stats = {
            'todayEvents': len(today_events),
            'weekEvents': len(week_events),
            'upcomingShowings': len(upcoming_showings),
            'tasksDue': len(tasks_due),
            'nextEvent': today_events[0].to_dict() if today_events else None
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Error fetching calendar stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch calendar stats'
        }), 500


@calendar_bp.route('/api/calendar/clients', methods=['GET'])
@api_login_required
def get_clients_for_calendar():
    """Get client list for event creation dropdown"""
    try:
        clients = Client.query.filter_by(
            user_id=current_user.id
        ).order_by(Client.first_name).all()
        
        client_list = [{
            'id': client.id,
            'name': f"{client.first_name} {client.last_name}",
            'email': client.email,
            'type': client.type
        } for client in clients]
        
        return jsonify({
            'success': True,
            'clients': client_list
        }), 200
        
    except Exception as e:
        print(f"Error fetching clients: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch clients'
        }), 500