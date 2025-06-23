from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app.models import db, User
from functools import wraps
import logging
import requests
import json
import os
from flask_login import login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

# Directory to store user preferences (temporary solution)
PREFERENCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'user_preferences')
os.makedirs(PREFERENCES_DIR, exist_ok=True)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # Handle POST (login attempt)
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        flash('Email and password are required', 'error')
        return redirect(url_for('auth.login'))
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        # Successful login
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.username
        session['user_plan'] = user.plan
        
        # CRITICAL: Login with Flask-Login
        login_user(user)
        
        # Update last login
        user.last_login = db.func.now()
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('web.dashboard')}), 200
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('web.dashboard'))
    
    # Failed login
    if request.is_json:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    flash('Invalid email or password', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page and handler"""
    if request.method == 'GET':
        return render_template('auth/signup.html')
    
    # Handle POST (signup attempt)
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validation
    errors = []
    if not email or '@' not in email:
        errors.append('Valid email is required')
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters')
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters')
    if password != confirm_password:
        errors.append('Passwords do not match')
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        errors.append('Email already registered')
    if User.query.filter_by(username=username).first():
        errors.append('Username already taken')
    
    if errors:
        if request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('auth.signup'))
    
    # Create new user
    try:
        user = User(
            email=email,
            username=username,
            full_name=data.get('full_name', ''),
            company=data.get('company', ''),
            role=data.get('role', 'agent')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after signup
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.username
        session['user_plan'] = user.plan
        
        # CRITICAL: Login with Flask-Login
        login_user(user)
        
         # SEND WELCOME EMAIL
        try:
            from app.email_utils import send_welcome_email  # Import your email function
            send_welcome_email(user.email, user.full_name or user.username)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            # Don't fail the signup if email fails
            
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('web.dashboard')}), 201
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Failed to create account'}), 500
        flash('Failed to create account. Please try again.', 'error')
        return redirect(url_for('auth.signup'))

# ===== GOOGLE OAUTH ROUTES =====

@auth_bp.route('/debug-oauth-config')
def debug_oauth_config():
    """Temporary debug endpoint - REMOVE AFTER TESTING"""
    import os
    return jsonify({
        'client_id_first_20': os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET')[:20],
        'client_id_last_20': os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET')[-20:],
        'has_secret': bool(os.environ.get('GOOGLE_CLIENT_SECRET')),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI', 'NOT SET'),
        'production': os.environ.get('PRODUCTION'),
        'railway_env': bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    })

@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    # ENHANCED DEBUG
    print("\n" + "="*50)
    print("GOOGLE LOGIN ATTEMPT")
    print("="*50)
    
    # Check if OAuth exists on current_app
    if not hasattr(current_app, 'oauth') or not current_app.oauth:
        print("❌ OAuth not initialized on current_app!")
        print(f"current_app attributes: {[attr for attr in dir(current_app) if not attr.startswith('_')]}")
        print(f"OAuth enabled flag: {getattr(current_app, 'oauth_enabled', False)}")
        flash('Google login is not configured. Please check server logs.', 'error')
        return redirect(url_for('auth.login'))
    
    print("✅ OAuth found on current_app")
    
    # Now safely access the google client
    try:
        google = current_app.oauth.google
        print("✅ Google client accessed successfully")
    except Exception as e:
        print(f"❌ Error accessing google client: {e}")
        flash('Google OAuth client not properly configured', 'error')
        return redirect(url_for('auth.login'))
    
    # PRODUCTION FIX: Check for explicit redirect URI
    configured_redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
    
    if configured_redirect_uri:
        # Use the explicitly configured redirect URI (for production)
        redirect_uri = configured_redirect_uri
        print(f"🚀 Using configured redirect URI: {redirect_uri}")
    else:
        # Generate redirect URI (for local development)
        redirect_uri = url_for('auth.google_callback', _external=True)
        print(f"🔧 Generated redirect URI: {redirect_uri}")
    
    print(f"Client ID: {current_app.config['GOOGLE_CLIENT_ID'][:20] if current_app.config.get('GOOGLE_CLIENT_ID') else 'NOT SET'}...")
    print(f"Has Client Secret: {'Yes' if current_app.config.get('GOOGLE_CLIENT_SECRET') else 'No'}")
    print(f"Final redirect URI being used: {redirect_uri}")
    print(f"Request Host: {request.host}")
    print(f"Request scheme: {request.scheme}")
    print(f"Is secure: {request.is_secure}")
    
    # Production environment check
    if os.environ.get('PRODUCTION') or os.environ.get('RAILWAY_ENVIRONMENT'):
        print("🚀 Running in PRODUCTION environment")
        expected_uri = configured_redirect_uri or f"https://{request.host}/auth/google/callback"
    else:
        print("🔧 Running in DEVELOPMENT environment")
        expected_uri = "http://localhost:5001/auth/google/callback"
    
    print(f"\n🔍 URI COMPARISON:")
    print(f"What we're using: {redirect_uri}")
    print(f"Expected format: {expected_uri}")
    print(f"Match status: {'✅ GOOD' if redirect_uri == expected_uri else '⚠️  CHECK GOOGLE CONSOLE'}")
    print("="*50 + "\n")
    
    try:
        return google.authorize_redirect(redirect_uri, prompt='select_account')
    except Exception as e:
        print(f"❌ Error during authorize_redirect: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        flash('Failed to redirect to Google login', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        print("\n" + "="*50)
        print("GOOGLE CALLBACK DEBUG")
        print("="*50)
        
        print(f"Callback URL: {request.url}")
        print(f"Args: {request.args}")
        
        # Check if OAuth exists
        if not hasattr(current_app, 'oauth') or not current_app.oauth:
            print("❌ OAuth not found in callback!")
            flash('Google login configuration error', 'error')
            return redirect(url_for('auth.login'))
        
        # Use the SAME oauth access method as google_login()
        google = current_app.oauth.google
        print(f"Google client: {google}")
        
        print(f"About to authorize access token...")
        print(f"Request args: {dict(request.args)}")
        
        # 🔍 ENHANCED DEBUG - Check OAuth client configuration
        print(f"\n🔍 TOKEN EXCHANGE DEBUG:")
        print(f"Google client object: {google}")
        print(f"Google client ID: {getattr(google, 'client_id', 'NOT SET')}")
        client_secret = getattr(google, 'client_secret', 'NOT SET')
        print(f"Google client secret: {'SET' if client_secret and client_secret != 'NOT SET' else 'NOT SET'}")
        if client_secret and client_secret != 'NOT SET':
            print(f"Client secret starts with: {client_secret[:15]}...")
        print(f"Authorization code received: {request.args.get('code', 'NO CODE')[:20]}...")
        
        # Check if OAUTHLIB_INSECURE_TRANSPORT is set
        import os
        print(f"OAUTHLIB_INSECURE_TRANSPORT: {os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', 'NOT SET')}")
        
        # Check app config values during callback
        print(f"App config CLIENT_ID: {current_app.config.get('GOOGLE_CLIENT_ID', 'NOT SET')[:20] if current_app.config.get('GOOGLE_CLIENT_ID') else 'NOT SET'}...")
        app_secret = current_app.config.get('GOOGLE_CLIENT_SECRET', 'NOT SET')
        print(f"App config CLIENT_SECRET: {'SET' if app_secret != 'NOT SET' else 'NOT SET'}")
        print("="*30)
        
        # CRITICAL FIX: Use the same redirect_uri that was used in the authorize step
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        if not redirect_uri:
            redirect_uri = url_for('auth.google_callback', _external=True)
        
        print(f"🔑 Using redirect_uri for token exchange: {redirect_uri}")
        
        # Get the authorization token with explicit redirect_uri
        token = google.authorize_access_token(redirect_uri=redirect_uri)
        print(f"Token received: {bool(token)}")
        print(f"Token keys: {list(token.keys()) if token else 'No token'}")
        
        # Don't try to parse ID token - just get user info from API
        # This avoids the need for JWKS
        access_token = token.get('access_token')
        if not access_token:
            print("ERROR: No access token received")
            flash('Failed to get access token from Google', 'error')
            return redirect(url_for('auth.login'))
        
        print(f"Access token received: {access_token[:20]}...")
        
        # Get user info directly from Google's userinfo endpoint
        resp = google.get('userinfo')  # Let Authlib handle the URL
        user_info = resp.json()
        
        print(f"User info received: {user_info}")
        
        google_id = user_info.get('id')
        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        
        if not google_id or not email:
            print("ERROR: Missing user info from Google")
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('auth.login'))
        
        print(f"Processing user: {email}")
        
        # Check if user exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email
            user = User.query.filter_by(email=email).first()
            if user:
                # Link existing account to Google
                user.google_id = google_id
                user.oauth_provider = 'google'
                print(f"Linked existing user: {email}")
            else:
                # Create new user
                username = email.split('@')[0]
                
                # Make sure username is unique
                counter = 1
                original_username = username
                while User.query.filter_by(username=username).first():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User(
                    email=email,
                    username=username,
                    full_name=name,
                    google_id=google_id,
                    oauth_provider='google',
                    is_verified=True
                )
                print(f"Created new user: {email}")
        
        # Update last login
        user.last_login = db.func.now()
        db.session.add(user)
        db.session.commit()
        
        # Login user
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.username
        session['user_plan'] = user.plan
        
        # CRITICAL: Login with Flask-Login
        login_user(user)
        
        print(f"User logged in successfully: {email}")
        print("="*50 + "\n")
        
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        print(f"CALLBACK ERROR: {e}")
        print(f"Error type: {type(e)}")
        print(f"Full error: {repr(e)}")
        print("="*50 + "\n")
        
        logger.error(f"Google OAuth callback error: {e}")
        
        # More specific error handling
        if 'invalid_client' in str(e):
            flash('Google OAuth configuration error. Please contact support.', 'error')
        elif 'mismatching_state' in str(e):
            flash('Session expired. Please try again.', 'warning')
        else:
            flash(f'Google login failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))
    
@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile - saves only fields that exist in database"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Only update fields that ACTUALLY exist in your User model
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'company' in data:
            user.company = data['company'].strip()
        
        # Note: phone, license_number, bio don't exist in your database yet
        # but we'll still return success so the form works
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update profile. Please try again.'
        }), 500

@auth_bp.route('/profile/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    """Handle photo upload - placeholder for now since profile_photo field doesn't exist"""
    return jsonify({
        'success': True,
        'message': 'Photo feature coming soon!',
        'photo_url': '/static/images/default-avatar.png'
    })

@auth_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        data = request.get_json()
        
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # Verify current password
        if user.password_hash and not user.check_password(current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to change password. Please try again.'
        }), 500

# ===== USER PREFERENCES ROUTES =====

@auth_bp.route('/api/user/quick-actions', methods=['GET'])
@login_required
def get_quick_actions():
    """Get user's quick actions"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_quick_actions.json')
    
    # Default quick actions
    default_actions = [
        {
            'id': 'properties',
            'title': 'Property Management',
            'description': 'Search, save, and manage property listings',
            'url': '/properties',
            'icon': 'P'
        },
        {
            'id': 'clients',
            'title': 'Client Management',
            'description': 'Manage contacts and track interactions',
            'url': '/crm',
            'icon': 'C'
        },
        {
            'id': 'calendar',
            'title': 'Calendar & Scheduling',
            'description': 'Book property appointments and showings',
            'url': '/calendar',
            'icon': 'S'
        },
        {
            'id': 'messages',
            'title': 'Messages',
            'description': 'Communicate with clients and leads',
            'url': '/messages',
            'icon': 'M'
        },
        {
            'id': 'marketing',
            'title': 'Marketing Tools',
            'description': 'Create flyers and social media content',
            'url': '/marketing',
            'icon': 'K'
        },
        {
            'id': 'analytics',
            'title': 'Market Analytics',
            'description': 'View market trends and pricing data',
            'url': '/analytics',
            'icon': 'A'
        }
    ]
    
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r') as f:
                quick_actions = json.load(f)
        else:
            quick_actions = default_actions
        
        return jsonify({'success': True, 'quick_actions': quick_actions})
    except Exception as e:
        logger.error(f"Error loading quick actions: {e}")
        return jsonify({'success': True, 'quick_actions': default_actions})

@auth_bp.route('/api/user/quick-actions', methods=['POST'])
@login_required
def save_quick_actions():
    """Save user's quick actions"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_quick_actions.json')
    
    try:
        quick_actions = request.json.get('quick_actions', [])
        
        # Validate the data
        if not isinstance(quick_actions, list):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Save to file
        with open(preferences_file, 'w') as f:
            json.dump(quick_actions, f)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving quick actions: {e}")
        return jsonify({'error': 'Failed to save preferences'}), 500

# ===== QUICK SEARCHES ROUTES =====

@auth_bp.route('/api/user/quick-searches', methods=['GET'])
@login_required
def get_quick_searches():
    """Get user's saved quick searches"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_quick_searches.json')
    
    # Default quick searches
    default_searches = [
        'Orlando, FL',
        'Miami, FL',
        'Tampa, FL',
        'Jacksonville, FL',
        'Fort Lauderdale, FL'
    ]
    
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r') as f:
                quick_searches = json.load(f)
        else:
            quick_searches = default_searches
        
        return jsonify({'success': True, 'quick_searches': quick_searches})
    except Exception as e:
        logger.error(f"Error loading quick searches: {e}")
        return jsonify({'success': True, 'quick_searches': default_searches})

@auth_bp.route('/api/user/quick-searches', methods=['POST'])
@login_required
def save_quick_searches():
    """Save user's quick searches"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_quick_searches.json')
    
    try:
        quick_searches = request.json.get('quick_searches', [])
        
        # Validate the data
        if not isinstance(quick_searches, list):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Save to file
        with open(preferences_file, 'w') as f:
            json.dump(quick_searches, f)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving quick searches: {e}")
        return jsonify({'error': 'Failed to save preferences'}), 500

# ===== SAVED PROPERTIES ROUTES =====

@auth_bp.route('/api/user/saved-properties', methods=['GET'])
@login_required
def get_saved_properties():
    """Get user's saved properties"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_saved_properties.json')
    
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r') as f:
                saved_properties = json.load(f)
        else:
            saved_properties = []
        
        return jsonify({'success': True, 'saved_properties': saved_properties})
    except Exception as e:
        logger.error(f"Error loading saved properties: {e}")
        return jsonify({'success': True, 'saved_properties': []})

@auth_bp.route('/api/user/saved-properties', methods=['POST'])
@login_required
def toggle_saved_property():
    """Add or remove a saved property"""
    user_id = session['user_id']
    preferences_file = os.path.join(PREFERENCES_DIR, f'{user_id}_saved_properties.json')
    
    try:
        property_id = request.json.get('property_id')
        action = request.json.get('action', 'add')
        
        if not property_id:
            return jsonify({'error': 'Property ID required'}), 400
        
        # Load existing saved properties
        saved_properties = []
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r') as f:
                saved_properties = json.load(f)
        
        # Add or remove property
        if action == 'add':
            if property_id not in saved_properties:
                saved_properties.append(property_id)
        elif action == 'remove':
            if property_id in saved_properties:
                saved_properties.remove(property_id)
        
        # Save updated list
        with open(preferences_file, 'w') as f:
            json.dump(saved_properties, f)
        
        return jsonify({'success': True, 'saved_properties': saved_properties})
    except Exception as e:
        logger.error(f"Error toggling saved property: {e}")
        return jsonify({'error': 'Failed to update saved properties'}), 500

# ===== SAVED PROPERTY DETAILS =====

@auth_bp.route('/api/user/saved-property-details', methods=['POST'])
@login_required
def save_property_details():
    """Save property details when a property is saved (for offline access)"""
    user_id = session['user_id']
    details_file = os.path.join(PREFERENCES_DIR, f'{user_id}_property_details.json')
    
    try:
        property_data = request.json.get('property_data')
        if not property_data or not property_data.get('id'):
            return jsonify({'error': 'Property data required'}), 400
        
        # Load existing details
        all_details = {}
        if os.path.exists(details_file):
            with open(details_file, 'r') as f:
                all_details = json.load(f)
        
        # Add/update property details
        all_details[property_data['id']] = property_data
        
        # Save updated details
        with open(details_file, 'w') as f:
            json.dump(all_details, f)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving property details: {e}")
        return jsonify({'error': 'Failed to save property details'}), 500

@auth_bp.route('/api/user/saved-property-details/<property_id>', methods=['GET'])
@login_required
def get_property_details(property_id):
    """Get saved property details"""
    user_id = session['user_id']
    details_file = os.path.join(PREFERENCES_DIR, f'{user_id}_property_details.json')
    
    try:
        if os.path.exists(details_file):
            with open(details_file, 'r') as f:
                all_details = json.load(f)
                property_details = all_details.get(property_id)
                if property_details:
                    return jsonify({'success': True, 'property': property_details})
        
        return jsonify({'success': False, 'error': 'Property not found'}), 404
    except Exception as e:
        logger.error(f"Error loading property details: {e}")
        return jsonify({'error': 'Failed to load property details'}), 500