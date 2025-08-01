from flask import Blueprint, render_template, request, jsonify, session
import requests
import os
from flask_login import login_required
from app.models import User, db
from flask import current_app

# Create the blueprint
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@web_bp.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@web_bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')

# Legal and Support pages
@web_bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@web_bp.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')

@web_bp.route('/support')
def support():
    """Support page"""
    return render_template('support.html')

# DEBUG ROUTES TO HELP FIX ADMIN ACCESS
@web_bp.route('/debug-user')
@login_required
def debug_user():
    """Debug current user info"""
    user = User.query.get(session['user_id'])
    return f"""
    <h2>Current Session Info:</h2>
    <p>User ID: {session.get('user_id')}</p>
    <p>Email in session: {session.get('user_email')}</p>
    <p>Username: {session.get('user_name')}</p>
    <p>Plan: {session.get('user_plan')}</p>
    <br>
    <h2>User from Database:</h2>
    <p>Email: {user.email if user else 'No user found'}</p>
    <p>Username: {user.username if user else 'No user found'}</p>
    <p>OAuth Provider: {user.oauth_provider if user else 'No user found'}</p>
    """

@web_bp.route('/check-routes')
def check_routes():
    """Check all registered routes"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    
    # Look for admin routes
    admin_routes = [r for r in routes if '/admin' in r]
    
    return f"""
    <h2>Admin Routes Found:</h2>
    <pre>{chr(10).join(admin_routes) if admin_routes else 'NO ADMIN ROUTES FOUND!'}</pre>
    <br>
    <h2>All Routes:</h2>
    <pre>{chr(10).join(sorted(routes))}</pre>
    """

@web_bp.route('/test-admin')
def test_admin():
    """Test admin access"""
    if 'user_id' not in session:
        return "NOT LOGGED IN"
    
    user = User.query.get(session['user_id'])
    if not user:
        return "USER NOT FOUND IN DATABASE"
    
    admin_emails = ['benjamindelarosa20@gmail.com']
    
    return f"""
    <h2>Admin Access Test:</h2>
    <p>Your email: {user.email}</p>
    <p>Admin emails: {admin_emails}</p>
    <p>Is admin? {user.email in admin_emails}</p>
    <p>Email match? {user.email == 'benjamindelarosa20@gmail.com'}</p>
    <br>
    <p>Try admin page: <a href="/admin/users">/admin/users</a></p>
    """

@web_bp.route('/debug-auth')
def debug_auth():
    from flask_login import current_user
    return f"""
    <h1>Debug Auth Info</h1>
    <p>Session user_id: {session.get('user_id')}</p>
    <p>Current user authenticated: {current_user.is_authenticated}</p>
    <p>Current user: {current_user}</p>
    <p>Session data: {dict(session)}</p>
    <hr>
    <p><a href="/dashboard">Dashboard</a> | <a href="/crm">CRM</a></p>
    """

@web_bp.route('/force-login')
def force_login():
    from flask_login import login_user, current_user
    from app.models import User
    
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            login_user(user)
            return f"Forced login for {user.email}. <a href='/crm'>Try CRM now</a>"
    return "No user found in session"

# Tool pages
@web_bp.route('/education')
@login_required
def education():
    """Education Center with video courses"""
    return render_template('tools/education.html')

@web_bp.route('/crm')
@login_required
def crm():
    """Client Management"""
    return render_template('tools/crm.html')

@web_bp.route('/calendar')
@login_required
def calendar():
    """Calendar & Scheduling"""
    return render_template('tools/calendar.html')

@web_bp.route('/messages')
@login_required
def messages():
    """Messages"""
    return render_template('tools/messages.html')

@web_bp.route('/marketing')
@login_required
def marketing():
    """Marketing Tools"""
    return render_template('tools/marketing.html')

@web_bp.route('/documents')
@login_required
def documents():
    """Documents & E-signature"""
    return render_template('tools/documents.html')

@web_bp.route('/analytics')
@login_required
def analytics():
    """Market Analytics"""
    return render_template('tools/analytics.html')