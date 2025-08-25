from flask import Flask
import logging
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models.client import Client
from app.models.calendar_event import CalendarEvent

load_dotenv() 

def create_app():
    app = Flask(__name__)
    
    # Configuration - FIXED: Using propinsight.db
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'sqlite:///propinsight.db')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Force HTTPS in production (Railway or any production environment)
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PRODUCTION'):
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        
        # Handle proxy headers from Railway
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        
        print("🚀 Running in PRODUCTION mode with HTTPS enabled")
    
    # Session Configuration - IMPORTANT FOR OAUTH
    app.config['SESSION_COOKIE_NAME'] = 'reo_pro_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = bool(os.environ.get('PRODUCTION', False))  # True in production
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Google OAuth Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Use explicit redirect URI if provided (for production)
    app.config['GOOGLE_REDIRECT_URI'] = os.environ.get('GOOGLE_REDIRECT_URI')
    
    print(f"🔍 OAuth Debug in __init__.py:")
    print(f"   Client ID: {app.config['GOOGLE_CLIENT_ID'][:20] if app.config['GOOGLE_CLIENT_ID'] else 'MISSING'}...")
    print(f"   Client Secret: {'SET' if app.config['GOOGLE_CLIENT_SECRET'] else 'MISSING'}")
    print(f"   Redirect URI: {app.config['GOOGLE_REDIRECT_URI'] or 'Will be generated dynamically'}")
    print(f"   Production mode: {os.environ.get('PRODUCTION', False)}")
    print(f"   Railway environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not on Railway')}")
    
    # Initialize database
    from app.models import db
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Where to redirect when login required
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        if user_id is None:
            return None
        try:
            user = User.query.get(int(user_id))
            return user
        except Exception as e:
            print(f"Error in user_loader: {e}")
            return None
    
    # Initialize OAuth
    try:
        print("🔧 Attempting to import Authlib...")
        from authlib.integrations.flask_client import OAuth
        print("✅ Authlib imported successfully")
        
        print("🔧 Creating OAuth instance...")
        oauth = OAuth()
        print("✅ OAuth instance created")
        
        print("🔧 Initializing OAuth with app...")
        oauth.init_app(app)
        print("✅ OAuth initialized with app")
        
        print("🔧 Registering Google client...")
        
        # Build Google OAuth configuration
        google_config = {
            'client_id': app.config['GOOGLE_CLIENT_ID'],
            'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
            'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration',
            'client_kwargs': {
                'scope': 'openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
            }
        }
        
        # In production, use explicit redirect URI
        if app.config['GOOGLE_REDIRECT_URI']:
            google_config['redirect_uri'] = app.config['GOOGLE_REDIRECT_URI']
            print(f"   Using explicit redirect URI: {app.config['GOOGLE_REDIRECT_URI']}")
        else:
            print("   Redirect URI will be generated dynamically")
        
        # Register Google OAuth client
        google = oauth.register(
            name='google',
            **google_config
        )
        
        print("✅ Google client registered")
        
        # Store oauth in app for access in routes
        app.oauth = oauth
        app.oauth_enabled = True
        
        # Verify oauth is properly attached
        if hasattr(app, 'oauth'):
            print("✅ app.oauth is set!")
            print(f"   OAuth instance: {app.oauth}")
            print(f"   Has google client: {hasattr(app.oauth, 'google')}")
        
        print("✅ OAuth configured successfully - Google login should work!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Run: pip install Authlib==1.2.1")
        app.oauth = None
        app.oauth_enabled = False
        
    except Exception as e:
        print(f"❌ OAuth configuration failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        app.oauth = None
        app.oauth_enabled = False
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Register blueprints
    from app.routers.routes import api_bp
    from app.routers.web_routes import web_bp
    from app.routers.auth_routes import auth_bp
    from app.routers.admin_routes import admin_bp
    from app.routers.client_routes import client_bp
    from app.routers.calendar_routes import calendar_bp
    from app.routers.education_routes import education_bp
   


    
    # FIXED: Correct import for Google Calendar
    try:
        from app.google_calendar import google_calendar_bp
        app.register_blueprint(web_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(client_bp)
        app.register_blueprint(calendar_bp)
        app.register_blueprint(google_calendar_bp) 
        app.register_blueprint(education_bp) 
        print("✅ All blueprints registered including Google Calendar")
    except ImportError as e:
        print(f"⚠️  Could not import Google Calendar module: {e}")
        print("   Make sure app/google_calendar.py exists and has no syntax errors")
        # Register other blueprints anyway
        app.register_blueprint(web_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(client_bp)
        app.register_blueprint(calendar_bp)
        print("✅ All blueprints registered (except Google Calendar)")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Log final configuration summary
    print("\n" + "="*50)
    print("🚀 Real Estate Office Pro initialized successfully!")
    print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"   OAuth enabled: {app.oauth_enabled}")
    print(f"   Production mode: {bool(os.environ.get('PRODUCTION'))}")
    print("="*50 + "\n")
    
    return app