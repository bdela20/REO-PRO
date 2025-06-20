# Create this file: app/admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from app.models import db, User
from app.routers.auth_routes import login_required
import csv
from io import StringIO
from datetime import datetime, date
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        current_user = User.query.get(session['user_id'])
        
        # IMPORTANT: Replace this with YOUR email address
        admin_emails = ['benjamindelarosa20@gmail.com']  # YOUR EMAIL HERE!
        
        if current_user.email not in admin_emails:
            flash('Admin access required', 'error')
            return redirect(url_for('web.dashboard'))
            
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/users')
@admin_required
def users():
    """View all registered users with sorting"""
    
    # Get sorting parameters from URL
    sort_by = request.args.get('sort', 'created_at')  # Default sort by join date
    order = request.args.get('order', 'desc')  # Default newest first
    
    # Define sortable columns and their corresponding model attributes
    sortable_columns = {
        'id': User.id,
        'username': User.username,
        'email': User.email,
        'full_name': User.full_name,
        'plan': User.plan,
        'created_at': User.created_at,
        'last_login': User.last_login,
        'oauth_provider': User.oauth_provider
    }
    
    # Validate sort column
    if sort_by not in sortable_columns:
        sort_by = 'created_at'
    
    # Validate order
    if order not in ['asc', 'desc']:
        order = 'desc'
    
    # Build the query with sorting
    query = User.query
    
    if order == 'desc':
        query = query.order_by(sortable_columns[sort_by].desc())
    else:
        query = query.order_by(sortable_columns[sort_by].asc())
    
    # Get all users with sorting applied
    users = query.all()
    
    # Get stats (unchanged)
    total_users = User.query.count()
    users_today = User.query.filter(
        db.func.date(User.created_at) == date.today()
    ).count()
    google_users = User.query.filter_by(oauth_provider='google').count()
    
    return render_template('admin/users.html', 
                         users=users,
                         total_users=total_users,
                         users_today=users_today,
                         google_users=google_users,
                         current_sort=sort_by,
                         current_order=order)

@admin_bp.route('/users/export')
@admin_required
def export_users():
    """Export users to CSV"""
    # Create CSV
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['ID', 'Username', 'Email', 'Full Name', 'Company', 'Role', 
                 'Plan', 'Sign-up Method', 'Created At', 'Last Login'])
    
    # Write user data
    users = User.query.all()
    for user in users:
        cw.writerow([
            user.id,
            user.username,
            user.email,
            user.full_name or '',
            user.company or '',
            user.role or '',
            user.plan,
            'Google' if user.oauth_provider == 'google' else 'Email',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=propinsight_users_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@admin_bp.route('/users/send-welcome', methods=['POST'])
@admin_required
def send_welcome_email_route():
    """Send welcome email to specific user"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        from app.email_utils import send_welcome_email
        success = send_welcome_email(user.email, user.full_name or user.username)
        
        if success:
            return jsonify({'message': 'Welcome email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email. Check email configuration.'}), 500
            
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/stats')
@admin_required
def user_stats():
    """Get user statistics as JSON"""
    from datetime import timedelta
    
    # Total users
    total_users = User.query.count()
    
    # Users by plan
    free_users = User.query.filter_by(plan='free').count()
    pro_users = User.query.filter_by(plan='pro').count()
    
    # Sign-up methods
    google_users = User.query.filter_by(oauth_provider='google').count()
    email_users = total_users - google_users
    
    # Activity stats
    active_today = User.query.filter(
        User.last_login >= datetime.now() - timedelta(days=1)
    ).count()
    
    active_week = User.query.filter(
        User.last_login >= datetime.now() - timedelta(days=7)
    ).count()
    
    active_month = User.query.filter(
        User.last_login >= datetime.now() - timedelta(days=30)
    ).count()
    
    # New users by day (last 7 days)
    new_users_by_day = []
    for i in range(7):
        day = date.today() - timedelta(days=i)
        count = User.query.filter(
            db.func.date(User.created_at) == day
        ).count()
        new_users_by_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return jsonify({
        'total_users': total_users,
        'plans': {
            'free': free_users,
            'pro': pro_users
        },
        'signup_methods': {
            'google': google_users,
            'email': email_users
        },
        'activity': {
            'today': active_today,
            'week': active_week,
            'month': active_month
        },
        'new_users_trend': new_users_by_day
    })

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    # This could be expanded with more admin features
    return redirect(url_for('admin.users'))


# Add this new route to your admin_routes.py

@admin_bp.route('/users/delete', methods=['POST'])
@admin_required
def delete_user():
    """Delete a user account"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Get current admin user
    current_admin = User.query.get(session['user_id'])
    
    # Find user to delete
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'error': 'User not found'}), 404
    
    # Safety check: Don't allow admin to delete themselves
    if user_to_delete.id == current_admin.id:
        return jsonify({'error': 'You cannot delete your own account'}), 400
    
    # Safety check: Don't allow deletion of other admins (optional)
    admin_emails = ['benjamindelarosa20@gmail.com']  # YOUR EMAIL HERE
    if user_to_delete.email in admin_emails:
        return jsonify({'error': 'Cannot delete admin accounts'}), 400
    
    try:
        # Store user info for response
        deleted_username = user_to_delete.username
        deleted_email = user_to_delete.email
        
        # Delete the user
        db.session.delete(user_to_delete)
        db.session.commit()
        
        logger.info(f"Admin {current_admin.email} deleted user {deleted_email}")
        
        return jsonify({
            'success': True,
            'message': f'User "{deleted_username}" has been deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user. Please try again.'}), 500

