from flask import Flask
import logging
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models.client import Client

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'sqlite:///propinsight.db')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session Configuration - IMPORTANT FOR OAUTH
    app.config['SESSION_COOKIE_NAME'] = 'propinsight_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Google OAuth Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_REDIRECT_URI'] = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    print(f"🔍 OAuth Debug in __init__.py:")
    print(f"   Client ID: {app.config['GOOGLE_CLIENT_ID'][:20] if app.config['GOOGLE_CLIENT_ID'] else 'MISSING'}...")
    print(f"   Client Secret: {app.config['GOOGLE_CLIENT_SECRET'][:10] if app.config['GOOGLE_CLIENT_SECRET'] else 'MISSING'}...")
    print(f"   Redirect URI: {app.config['GOOGLE_REDIRECT_URI']}")
    
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
        print(f"=== USER LOADER CALLED with user_id: {user_id}, type: {type(user_id)} ===")
        if user_id is None:
            print("User ID is None")
            return None
        try:
            user = User.query.get(int(user_id))
            print(f"User found: {user}")
            if user:
                print(f"User email: {user.email}")
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
        
        print("🔧 Registering Google client with discovery URL...")
        # Use Google's discovery endpoint - this provides all needed URLs including jwks_uri
        google = oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            # Use discovery URL instead of static config
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            },
            # Force the redirect URI
            redirect_uri=app.config['GOOGLE_REDIRECT_URI']
        )
        print("✅ Google client registered with discovery URL")
        
        # Store oauth in app for access in routes
        app.oauth = oauth
        app.oauth_enabled = True
        
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
        app.oauth = None
        app.oauth_enabled = False
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    from app.routers.routes import api_bp
    from app.routers.web_routes import web_bp
    from app.routers.auth_routes import auth_bp
    from app.routers.admin_routes import admin_bp
    from app.routers.comparison_routes import comparison_bp
    from app.routers.client_routes import client_bp

    
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(client_bp)

    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # In app/__init__.py, update the user loader:
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        print(f"DEBUG: Loading user with ID: {user_id}")
        user = User.query.get(int(user_id))
        print(f"DEBUG: User found: {user is not None}")
        return user
    
    return app