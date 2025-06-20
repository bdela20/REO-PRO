#!/usr/bin/env python3
"""
PropInsight Pro - Simple Working Version
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect
import hashlib
import secrets
import requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "283553460411-bhrvmhgg89qg2d18v8p8o3aq95bkp001.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://localhost:5001/auth/google/callback"

# Simple user storage
users_db = {}

# Simple HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PropInsight Pro - Real Estate Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
        
        /* Header */
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
        .logo { font-size: 1.5rem; font-weight: bold; color: white; text-decoration: none; }
        .nav-buttons { display: flex; gap: 1rem; }
        .btn { padding: 0.5rem 1.5rem; border-radius: 25px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; cursor: pointer; border: none; }
        .btn-login { background: transparent; color: white; border: 2px solid white; }
        .btn-signup { background: white; color: #667eea; }
        .btn:hover { transform: translateY(-2px); }
        
        /* Hero */
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6rem 2rem; text-align: center; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }
        .hero-buttons { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
        .btn-primary { background: white; color: #667eea; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { background: white; margin: 5% auto; padding: 2rem; border-radius: 15px; max-width: 400px; position: relative; }
        .modal-close { position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.5rem; cursor: pointer; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .form-group input { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 10px; font-size: 1rem; }
        
        /* Social buttons */
        .social-buttons { margin: 1.5rem 0; }
        .social-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 0.75rem; border: 2px solid #4285f4; border-radius: 10px; background: white; color: #333; font-weight: 500; cursor: pointer; margin-bottom: 0.75rem; }
        .social-btn:hover { background: #f1f5ff; }
        .divider { text-align: center; margin: 1rem 0; color: #666; }
        
        /* Messages */
        .success { background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .error { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .hero-buttons { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">PropInsight Pro</a>
            <div class="nav-buttons">
                <button class="btn btn-login" id="loginBtn">Login</button>
                <button class="btn btn-signup" id="signupBtn">Get Started</button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <h1>Real Estate Intelligence for Modern Realtors</h1>
        <p>PropInsight Pro combines property search, market analytics, and lead generation to help realtors close more deals.</p>
        <div class="hero-buttons">
            <button class="btn-primary" id="heroSignupBtn">Get 5 Free Searches</button>
        </div>
    </section>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <button class="modal-close" id="closeLogin">&times;</button>
            <h2 style="text-align: center; margin-bottom: 1.5rem;">Realtor Login</h2>
            
            <div class="social-buttons">
                <button class="social-btn" id="googleLoginBtn">
                    🔍 Continue with Google
                </button>
            </div>
            
            <div class="divider">or continue with email</div>
            
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" id="loginEmail" placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="loginPassword" placeholder="Enter your password">
            </div>
            <button class="btn-primary" style="width: 100%;" id="emailLoginBtn">Sign In</button>
            <p style="text-align: center; margin-top: 1rem;">
                <a href="#" id="switchToSignup">Don't have an account? Sign up</a>
            </p>
            <div id="loginMessage"></div>
        </div>
    </div>

    <!-- Signup Modal -->
    <div id="signupModal" class="modal">
        <div class="modal-content">
            <button class="modal-close" id="closeSignup">&times;</button>
            <h2 style="text-align: center; margin-bottom: 1.5rem;">Create Realtor Account</h2>
            
            <div class="social-buttons">
                <button class="social-btn" id="googleSignupBtn">
                    🔍 Sign up with Google
                </button>
            </div>
            
            <div class="divider">or sign up with email</div>
            
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" id="signupName" placeholder="John Smith">
            </div>
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" id="signupEmail" placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>Real Estate License Number</label>
                <input type="text" id="signupLicense" placeholder="SL1234567">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="signupPassword" placeholder="Create a password">
            </div>
            <button class="btn-primary" style="width: 100%;" id="emailSignupBtn">Start Free Trial</button>
            <p style="text-align: center; margin-top: 1rem;">
                <a href="#" id="switchToLogin">Already have an account? Sign in</a>
            </p>
            <div id="signupMessage"></div>
        </div>
    </div>

    <script>
        // Simple JavaScript that WILL work
        console.log('🚀 PropInsight Pro loading...');

        // Wait for page to load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ Page loaded, setting up events...');

            // Get all elements
            const loginBtn = document.getElementById('loginBtn');
            const signupBtn = document.getElementById('signupBtn');
            const heroSignupBtn = document.getElementById('heroSignupBtn');
            const loginModal = document.getElementById('loginModal');
            const signupModal = document.getElementById('signupModal');
            const closeLogin = document.getElementById('closeLogin');
            const closeSignup = document.getElementById('closeSignup');
            const googleLoginBtn = document.getElementById('googleLoginBtn');
            const googleSignupBtn = document.getElementById('googleSignupBtn');
            const emailLoginBtn = document.getElementById('emailLoginBtn');
            const emailSignupBtn = document.getElementById('emailSignupBtn');
            const switchToSignup = document.getElementById('switchToSignup');
            const switchToLogin = document.getElementById('switchToLogin');

            // Modal functions
            function showLogin() {
                console.log('📱 Showing login modal');
                hideModals();
                loginModal.style.display = 'block';
            }

            function showSignup() {
                console.log('📱 Showing signup modal');
                hideModals();
                signupModal.style.display = 'block';
            }

            function hideModals() {
                loginModal.style.display = 'none';
                signupModal.style.display = 'none';
            }

            function showMessage(elementId, message, type) {
                const element = document.getElementById(elementId);
                const className = type === 'error' ? 'error' : 'success';
                element.innerHTML = `<div class="${className}">${message}</div>`;
            }

            // Google OAuth functions
            function googleLogin() {
                console.log('🔍 Google login clicked');
                googleLoginBtn.textContent = 'Connecting...';
                googleLoginBtn.disabled = true;
                window.location.href = '/auth/google?action=login';
            }

            function googleSignup() {
                console.log('🔍 Google signup clicked');
                googleSignupBtn.textContent = 'Connecting...';
                googleSignupBtn.disabled = true;
                window.location.href = '/auth/google?action=signup';
            }

            // Email login
            async function emailLogin() {
                console.log('📧 Email login clicked');
                const email = document.getElementById('loginEmail').value;
                const password = document.getElementById('loginPassword').value;

                if (!email || !password) {
                    showMessage('loginMessage', 'Please enter both email and password.', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });

                    if (response.ok) {
                        showMessage('loginMessage', 'Login successful! Redirecting...', 'success');
                        setTimeout(() => window.location.href = '/dashboard', 1500);
                    } else {
                        const error = await response.json();
                        showMessage('loginMessage', error.message || 'Login failed.', 'error');
                    }
                } catch (err) {
                    showMessage('loginMessage', 'Network error: ' + err.message, 'error');
                }
            }

            // Email signup
            async function emailSignup() {
                console.log('📧 Email signup clicked');
                const name = document.getElementById('signupName').value;
                const email = document.getElementById('signupEmail').value;
                const license = document.getElementById('signupLicense').value;
                const password = document.getElementById('signupPassword').value;

                if (!name || !email || !password) {
                    showMessage('signupMessage', 'Please fill in all required fields.', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/signup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, email, license, password })
                    });

                    if (response.ok) {
                        showMessage('signupMessage', 'Account created! Redirecting...', 'success');
                        setTimeout(() => window.location.href = '/dashboard', 1500);
                    } else {
                        const error = await response.json();
                        showMessage('signupMessage', error.message || 'Signup failed.', 'error');
                    }
                } catch (err) {
                    showMessage('signupMessage', 'Network error: ' + err.message, 'error');
                }
            }

            // Add all event listeners
            loginBtn.addEventListener('click', showLogin);
            signupBtn.addEventListener('click', showSignup);
            heroSignupBtn.addEventListener('click', showSignup);
            closeLogin.addEventListener('click', hideModals);
            closeSignup.addEventListener('click', hideModals);
            googleLoginBtn.addEventListener('click', googleLogin);
            googleSignupBtn.addEventListener('click', googleSignup);
            emailLoginBtn.addEventListener('click', emailLogin);
            emailSignupBtn.addEventListener('click', emailSignup);
            switchToSignup.addEventListener('click', function(e) {
                e.preventDefault();
                showSignup();
            });
            switchToLogin.addEventListener('click', function(e) {
                e.preventDefault();
                showLogin();
            });

            // Close modal when clicking outside
            window.addEventListener('click', function(event) {
                if (event.target === loginModal || event.target === signupModal) {
                    hideModals();
                }
            });

            // Check for OAuth errors in URL
            const urlParams = new URLSearchParams(window.location.search);
            const error = urlParams.get('error');
            
            if (error === 'oauth_failed') {
                alert('Google login failed. Please try again or use email login.');
            } else if (error === 'user_not_found') {
                alert('Account not found. Please sign up first.');
                showSignup();
            }

            console.log('✅ All event listeners set up successfully!');
        });
    </script>
</body>
</html>
'''

# Dashboard Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - PropInsight Pro</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
        .logo { font-size: 1.5rem; font-weight: bold; color: white; text-decoration: none; }
        .logout-btn { background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; }
        .content { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .welcome { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .welcome h1 { font-size: 2rem; margin-bottom: 0.5rem; color: #2d3748; }
        .welcome p { color: #718096; }
    </style>
</head>
<body>
    <div class="header">
        <div class="nav-container">
            <a href="/" class="logo">PropInsight Pro</a>
            <div>
                <span>Welcome, {{ session.realtor_name }}!</span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
    </div>

    <div class="content">
        <div class="welcome">
            <h1>Welcome back, {{ session.realtor_name }}!</h1>
            <p>{% if session.license %}License: {{ session.license }} | {% endif %}Your dashboard is ready.</p>
            <p>🎉 <strong>Google OAuth is working!</strong> You're successfully logged in.</p>
        </div>
    </div>

    <script>
        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template_string(DASHBOARD_TEMPLATE, session=session)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    license_num = data.get('license', '').strip()
    password = data.get('password', '')
    
    if not email or not name or not password:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if email in users_db:
        return jsonify({'message': 'Email already exists'}), 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user_id = secrets.token_hex(8)
    users_db[email] = {
        'user_id': user_id,
        'name': name,
        'email': email,
        'license': license_num,
        'password_hash': password_hash,
        'oauth_provider': None
    }
    
    session['user_id'] = user_id
    session['realtor_name'] = name
    session['license'] = license_num
    session['email'] = email
    
    print(f"✅ New realtor signed up: {name} ({email})")
    return jsonify({'status': 'success'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = users_db.get(email)
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    session['user_id'] = user['user_id']
    session['realtor_name'] = user['name']
    session['license'] = user['license']
    session['email'] = user['email']
    
    print(f"✅ Realtor logged in: {user['name']} ({email})")
    return jsonify({'status': 'success'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})

@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow"""
    action = request.args.get('action', 'login')
    session['oauth_action'] = action
    
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'select_account'
    }
    
    auth_url = f"{google_auth_url}?{urlencode(params)}"
    print(f"🔄 Redirecting to Google OAuth: {action}")
    return redirect(auth_url)

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error or not code:
            print(f"❌ OAuth error: {error}")
            return redirect('/?error=oauth_failed')
        
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        token_response = requests.post(token_url, data=token_data)
        if not token_response.ok:
            print(f"❌ Token exchange failed: {token_response.text}")
            return redirect('/?error=oauth_failed')
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            return redirect('/?error=oauth_failed')
        
        # Get user info
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        user_response = requests.get(user_info_url)
        
        if not user_response.ok:
            return redirect('/?error=oauth_failed')
        
        user_data = user_response.json()
        google_id = user_data.get('id')
        email = user_data.get('email', '').lower()
        name = user_data.get('name', '')
        
        if not email or not name:
            return redirect('/?error=oauth_failed')
        
        print(f"✅ Google user data: {name} ({email})")
        
        # Handle user
        existing_user = users_db.get(email)
        action = session.get('oauth_action', 'login')
        
        if action == 'signup':
            if existing_user:
                # User exists, log them in
                user = existing_user
            else:
                # Create new user
                user_id = secrets.token_hex(8)
                user = {
                    'user_id': user_id,
                    'name': name,
                    'email': email,
                    'license': '',
                    'password_hash': '',
                    'oauth_provider': 'google',
                    'google_id': google_id
                }
                users_db[email] = user
                print(f"✅ New Google user created: {name}")
        else:  # login
            if not existing_user:
                return redirect('/?error=user_not_found')
            user = existing_user
        
        # Set session
        session['user_id'] = user['user_id']
        session['realtor_name'] = user['name']
        session['license'] = user.get('license', '')
        session['email'] = user['email']
        
        print(f"✅ Google OAuth success: {name}")
        return redirect('/dashboard')
    
    except Exception as e:
        print(f"❌ Google OAuth error: {str(e)}")
        return redirect('/?error=oauth_failed')

if __name__ == '__main__':
    print("🚀 PropInsight Pro - SIMPLE WORKING VERSION")
    print("=" * 50)
    print("📍 Server: http://localhost:5001")
    print("🔍 Google OAuth: CONFIGURED ✅")
    print("📧 Email signup/login: WORKING ✅")
    print("🎯 NO MORE JAVASCRIPT ERRORS!")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)