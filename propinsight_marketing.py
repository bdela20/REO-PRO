#!/usr/bin/env python3
"""
PropInsight Pro - Professional Real Estate Platform
Marketing Website with Landing Page
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect
import os
import sys
import hashlib
import secrets

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Simple in-memory user storage
users_db = {}

# Professional Marketing Website Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if page_title %}{{ page_title }} - {% endif %}PropInsight Pro - Real Estate Intelligence Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }

        /* Navigation */
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }

        .logo {
            display: flex;
            align-items: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #2d3748;
            text-decoration: none;
        }

        .nav-menu {
            display: flex;
            list-style: none;
            gap: 2rem;
            align-items: center;
        }

        .nav-link {
            color: #4a5568;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .nav-link:hover, .nav-link.active {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }

        .nav-buttons {
            display: flex;
            gap: 1rem;
        }

        /* Mobile Menu */
        .mobile-menu-toggle {
            display: none;
            flex-direction: column;
            cursor: pointer;
            padding: 0.5rem;
        }

        .mobile-menu-toggle span {
            width: 25px;
            height: 3px;
            background: #2d3748;
            margin: 3px 0;
            transition: 0.3s;
        }

        .mobile-menu-toggle.active span:nth-child(1) {
            transform: rotate(-45deg) translate(-5px, 6px);
        }

        .mobile-menu-toggle.active span:nth-child(2) {
            opacity: 0;
        }

        .mobile-menu-toggle.active span:nth-child(3) {
            transform: rotate(45deg) translate(-5px, -6px);
        }

        .mobile-nav {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            width: 100%;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }

        .mobile-nav.active {
            display: block;
        }

        .mobile-nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .mobile-nav li {
            text-align: center;
            padding: 0.5rem 0;
        }

        .mobile-nav .nav-link {
            display: block;
            padding: 1rem;
            font-size: 1.1rem;
        }

        .mobile-nav .nav-buttons {
            justify-content: center;
            margin-top: 1rem;
            padding: 0 2rem;
        }

        .btn-login {
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-login:hover {
            background: #667eea;
            color: white;
        }

        .btn-signup {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-signup:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }

        /* Main Content */
        .main-content {
            margin-top: 80px;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6rem 0;
            text-align: center;
        }

        .hero-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }

        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }

        .hero-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn-primary {
            background: white;
            color: #667eea;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }

        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }

        .btn-secondary {
            background: transparent;
            color: white;
            border: 2px solid white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }

        .btn-secondary:hover {
            background: white;
            color: #667eea;
        }

        /* Hero Search */
        .hero-search-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
        }

        .hero-search {
            display: flex;
            gap: 1rem;
            max-width: 600px;
            margin: 0 auto;
            position: relative;
        }

        .search-wrapper {
            flex: 1;
            position: relative;
        }

        .hero-search-input {
            width: 100%;
            padding: 1rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            outline: none;
        }

        .hero-search-btn {
            background: white;
            color: #667eea;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.3s ease;
        }

        .hero-search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        /* Autocomplete Dropdown */
        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            z-index: 1000;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            margin-top: 5px;
        }

        .autocomplete-dropdown.show {
            display: block;
        }

        .autocomplete-item {
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s ease;
            color: #333;
        }

        .autocomplete-item:hover, .autocomplete-item.selected {
            background-color: #f8f9fa;
        }

        .autocomplete-item:last-child {
            border-bottom: none;
        }

        .autocomplete-main {
            font-weight: 600;
            margin-bottom: 2px;
        }

        .autocomplete-secondary {
            font-size: 0.85em;
            color: #666;
        }

        /* Dashboard Search */
        .search-wrapper-dashboard {
            position: relative;
            flex: 1;
        }

        .hero-search-results {
            margin-top: 2rem;
            text-align: left;
        }

        .hero-property-card {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }

        .trial-banner {
            background: linear-gradient(45deg, #48bb78, #38a169);
            color: white;
            padding: 1rem;
            text-align: center;
            border-radius: 10px;
            margin: 1rem 0;
            font-weight: 600;
        }

        .upgrade-prompt {
            background: linear-gradient(45deg, #ed8936, #dd6b20);
            color: white;
            padding: 1.5rem;
            text-align: center;
            border-radius: 15px;
            margin: 2rem 0;
        }

        .upgrade-prompt h3 {
            margin-bottom: 1rem;
        }

        .upgrade-prompt button {
            background: white;
            color: #dd6b20;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            margin: 0 0.5rem;
        }

        /* Social Login Styles */
        .social-login-section {
            margin: 1.5rem 0;
            text-align: center;
        }

        .social-login-divider {
            display: flex;
            align-items: center;
            margin: 1.5rem 0;
            color: #666;
        }

        .social-login-divider::before,
        .social-login-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #e2e8f0;
        }

        .social-login-divider span {
            padding: 0 1rem;
            font-size: 0.9rem;
        }

        .social-login-buttons {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .social-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            background: white;
            color: #333;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .social-btn:hover {
            border-color: #667eea;
            background: #f8f9ff;
            transform: translateY(-1px);
        }

        .social-btn img {
            width: 20px;
            height: 20px;
            margin-right: 0.75rem;
        }

        .social-btn-google {
            border-color: #4285f4;
        }

        .social-btn-google:hover {
            background: #f1f5ff;
            border-color: #4285f4;
        }

        .social-btn-microsoft {
            border-color: #0078d4;
        }

        .social-btn-microsoft:hover {
            background: #f1f8ff;
            border-color: #0078d4;
        }

        .social-btn-linkedin {
            border-color: #0077b5;
        }

        .social-btn-linkedin:hover {
            background: #f0f8ff;
            border-color: #0077b5;
        }

        /* Sections */
        .section {
            padding: 5rem 0;
        }

        .section-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .section h2 {
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 3rem;
            color: #2d3748;
        }

        /* Updated Features Grid - Aligned Layout */
        .features-grid-aligned {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin-top: 3rem;
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Bottom row item - spans all 3 columns and centers itself */
        .features-grid-aligned .feature-card.bottom-row {
            grid-column: 1 / -1;
            max-width: 320px;
            margin: 0 auto;
            margin-top: 1rem;
        }

        /* Regular Features Grid (for other pages) */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }

        .feature-icon {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
        }

        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #2d3748;
        }

        .feature-card p {
            color: #718096;
        }

        /* About Section */
        .about {
            background: #f8fafc;
        }

        .about-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }

        .about-text h3 {
            font-size: 1.8rem;
            margin-bottom: 1rem;
            color: #2d3748;
        }

        .about-text p {
            margin-bottom: 1rem;
            color: #4a5568;
            font-size: 1.1rem;
        }

        .about-image {
            text-align: center;
            font-size: 8rem;
            color: #667eea;
        }

        /* Pricing Section */
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .pricing-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            position: relative;
            transition: all 0.3s ease;
        }

        .pricing-card:hover {
            transform: translateY(-5px);
        }

        .pricing-card.featured {
            border: 3px solid #667eea;
            transform: scale(1.05);
        }

        .pricing-badge {
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            font-weight: 600;
        }

        .pricing-price {
            font-size: 3rem;
            font-weight: bold;
            color: #2d3748;
            margin: 1rem 0;
        }

        .pricing-features {
            list-style: none;
            margin: 2rem 0;
        }

        .pricing-features li {
            padding: 0.5rem 0;
            color: #4a5568;
        }

        .pricing-features li:before {
            content: "✓";
            color: #48bb78;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        /* Footer */
        .footer {
            background: #2d3748;
            color: white;
            padding: 3rem 0 1rem 0;
            text-align: center;
        }

        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .footer p {
            margin-bottom: 1rem;
        }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
        }

        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 15px;
            max-width: 400px;
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #2d3748;
        }

        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Page Styles */
        .page {
            display: none;
        }

        .page.active {
            display: block;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .nav-menu, .nav-buttons {
                display: none;
            }

            .mobile-menu-toggle {
                display: flex;
            }

            .navbar {
                position: relative;
            }

            .hero h1 {
                font-size: 2.5rem;
            }

            .hero-buttons {
                flex-direction: column;
                align-items: center;
            }

            .about-content {
                grid-template-columns: 1fr;
                text-align: center;
            }

            .pricing-card.featured {
                transform: none;
            }

            .hero-search {
                flex-direction: column;
            }

            .hero-search-btn {
                padding: 1rem;
            }

            .hero-search-container {
                padding: 1.5rem;
            }

            .search-form {
                flex-direction: column;
                gap: 1rem;
            }

            /* Mobile responsive for aligned features */
            .features-grid-aligned {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
            
            .features-grid-aligned .feature-card.bottom-row {
                grid-column: 1;
                max-width: none;
                margin-top: 0;
            }
        }

        @media (max-width: 992px) and (min-width: 769px) {
            .features-grid-aligned {
                grid-template-columns: repeat(2, 1fr);
                max-width: 700px;
            }
            
            .features-grid-aligned .feature-card.bottom-row {
                grid-column: 1 / -1;
                max-width: 320px;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="#" class="logo" onclick="showPage('home')">
                PropInsight Pro
            </a>
            <ul class="nav-menu">
                <li><a class="nav-link active" onclick="showPage('home')">Home</a></li>
                <li><a class="nav-link" onclick="showPage('features')">Features</a></li>
                <li><a class="nav-link" onclick="showPage('about')">About</a></li>
                <li><a class="nav-link" onclick="showPage('pricing')">Pricing</a></li>
                <li><a class="nav-link" onclick="showPage('contact')">Contact</a></li>
            </ul>
            <div class="nav-buttons">
                <a href="#" class="btn-login" onclick="showLogin()">Login</a>
                <a href="#" class="btn-signup" onclick="showSignup()">Get Started</a>
            </div>
            <div class="mobile-menu-toggle" onclick="toggleMobileMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        <div class="mobile-nav" id="mobileNav">
            <ul>
                <li><a class="nav-link" onclick="showPage('home'); closeMobileMenu()">Home</a></li>
                <li><a class="nav-link" onclick="showPage('features'); closeMobileMenu()">Features</a></li>
                <li><a class="nav-link" onclick="showPage('about'); closeMobileMenu()">About</a></li>
                <li><a class="nav-link" onclick="showPage('pricing'); closeMobileMenu()">Pricing</a></li>
                <li><a class="nav-link" onclick="showPage('contact'); closeMobileMenu()">Contact</a></li>
            </ul>
            <div class="nav-buttons">
                <a href="#" class="btn-login" onclick="showLogin(); closeMobileMenu()">Login</a>
                <a href="#" class="btn-signup" onclick="showSignup(); closeMobileMenu()">Get Started</a>
            </div>
        </div>
    </nav>

    <div class="main-content">
        <!-- Home Page -->
        <div id="home" class="page active">
            <!-- Hero Section -->
            <section class="hero">
                <div class="hero-container">
                    <h1>Real Estate Intelligence for Modern Realtors</h1>
                    <p>PropInsight Pro combines property search, market analytics, and lead generation to help realtors close more deals and grow their business.</p>
                    
                    <!-- Free Search Bar -->
                    <div class="hero-search-container">
                        <h3 style="margin-bottom: 1rem; color: white;">Try It Free - Search Any Property</h3>
                        <div class="hero-search">
                            <div class="search-wrapper">
                                <input type="text" id="heroLocation" class="hero-search-input" placeholder="Enter city or address (e.g., Orlando, FL)" autocomplete="off">
                                <div class="autocomplete-dropdown" id="heroAutocomplete"></div>
                            </div>
                            <button class="hero-search-btn" onclick="heroSearch()">Search Properties</button>
                        </div>
                        <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">No signup required for your first search</p>
                        <div id="heroSearchResults" class="hero-search-results"></div>
                    </div>
                    
                    <div class="hero-buttons" style="margin-top: 2rem;">
                        <button class="btn-primary" onclick="showSignup()">Get 5 Free Searches</button>
                        <a href="#" class="btn-secondary" onclick="showPage('features')">See Features</a>
                    </div>
                </div>
            </section>

            <!-- Features Preview - Updated Layout -->
            <section class="section">
                <div class="section-container">
                    <h2>Everything You Need to Succeed</h2>
                    <div class="features-grid-aligned">
                        <!-- Top row: 3 items -->
                        <div class="feature-card">
                            <div class="feature-icon">SEARCH</div>
                            <h3>Property Search</h3>
                            <p>Search properties with real market data, rent estimates, and detailed analytics.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">TOOLS</div>
                            <h3>Business Tools</h3>
                            <p>CRM, commission tracking, and marketing tools to grow your business.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">LEADS</div>
                            <h3>Lead Generation</h3>
                            <p>Find motivated sellers, first-time buyers, and investment opportunities.</p>
                        </div>
                        
                        <!-- Bottom row: 1 item centered -->
                        <div class="feature-card bottom-row">
                            <div class="feature-icon">REPORTS</div>
                            <h3>Market Reports</h3>
                            <p>Professional market analysis and neighborhood insights for client presentations.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Features Page -->
        <div id="features" class="page">
            <section class="section">
                <div class="section-container">
                    <h2>Powerful Features for Real Estate Professionals</h2>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">DATA</div>
                            <h3>Real Property Data</h3>
                            <p>Access real-time property information, rent estimates, and market valuations from trusted sources.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">LEADS</div>
                            <h3>Smart Lead Generation</h3>
                            <p>Identify hot seller leads, investment opportunities, and first-time buyer properties.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">ANALYTICS</div>
                            <h3>Market Intelligence</h3>
                            <p>Comprehensive neighborhood analysis, price trends, and market forecasting.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">CRM</div>
                            <h3>Client Management</h3>
                            <p>Built-in CRM to track leads, manage clients, and automate follow-ups.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">METRICS</div>
                            <h3>Business Analytics</h3>
                            <p>Track commissions, analyze performance, and set business goals.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">MARKETING</div>
                            <h3>Marketing Tools</h3>
                            <p>Professional templates, social media content, and client presentation materials.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- About Page -->
        <div id="about" class="page">
            <section class="section about">
                <div class="section-container">
                    <h2>Built by a Realtor, for Realtors</h2>
                    <div class="about-content">
                        <div class="about-text">
                            <h3>The PropInsight Story</h3>
                            <p>PropInsight Pro was created by experienced real estate professionals who understand the challenges agents face in today's competitive market.</p>
                            <p>After struggling with expensive, complex tools that didn't meet industry needs, our team combined real estate expertise with technology skills to build the platform agents actually want to use.</p>
                            <p>Today, PropInsight Pro helps realtors across the United States find leads, analyze markets, and grow their businesses with tools designed by professionals who understand your daily challenges.</p>
                            <p><strong>Built by realtors, for realtors.</strong></p>
                        </div>
                        <div class="about-image" style="font-size: 4rem; color: #667eea; font-weight: bold;">
                            REALTOR
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Pricing Page -->
        <div id="pricing" class="page">
            <section class="section">
                <div class="section-container">
                    <h2>Simple, Transparent Pricing</h2>
                    <div class="pricing-grid">
                        <div class="pricing-card">
                            <h3>Starter</h3>
                            <div class="pricing-price">$9<span style="font-size: 1rem;">/month</span></div>
                            <ul class="pricing-features">
                                <li>50 property searches/month</li>
                                <li>Basic market reports</li>
                                <li>Property analytics</li>
                                <li>Email support</li>
                                <li>Mobile app access</li>
                            </ul>
                            <button class="btn-primary" onclick="showSignup()">Start Free Trial</button>
                        </div>
                        <div class="pricing-card featured">
                            <div class="pricing-badge">Most Popular</div>
                            <h3>Professional</h3>
                            <div class="pricing-price">$19<span style="font-size: 1rem;">/month</span></div>
                            <ul class="pricing-features">
                                <li>Unlimited property searches</li>
                                <li>Lead generation tools</li>
                                <li>Advanced market analytics</li>
                                <li>Client CRM system</li>
                                <li>Professional reports</li>
                                <li>Priority support</li>
                                <li>Export data to Excel</li>
                            </ul>
                            <button class="btn-primary" onclick="showSignup()">Start Free Trial</button>
                        </div>
                        <div class="pricing-card">
                            <h3>Team</h3>
                            <div class="pricing-price">$39<span style="font-size: 1rem;">/month</span></div>
                            <ul class="pricing-features">
                                <li>Everything in Professional</li>
                                <li>Up to 5 team members</li>
                                <li>Team collaboration tools</li>
                                <li>Custom branding</li>
                                <li>Phone support</li>
                                <li>Training & onboarding</li>
                                <li>API access</li>
                            </ul>
                            <button class="btn-primary" onclick="showSignup()">Start Free Trial</button>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Contact Page -->
        <div id="contact" class="page">
            <section class="section">
                <div class="section-container">
                    <h2>Get in Touch</h2>
                    <div style="max-width: 600px; margin: 0 auto; text-align: center;">
                        <p style="font-size: 1.2rem; margin-bottom: 2rem;">Have questions about PropInsight Pro? We're here to help!</p>
                        
                        <div class="feature-card" style="margin-bottom: 2rem;">
                            <h3>Email Support</h3>
                            <p>support@propinsight.pro</p>
                        </div>
                        
                        <div class="feature-card" style="margin-bottom: 2rem;">
                            <h3>Phone Support</h3>
                            <p>Available for Professional and Team plans</p>
                        </div>
                        
                        <div class="feature-card">
                            <h3>Business Inquiries</h3>
                            <p>info@propinsight.pro</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <p>&copy; 2025 PropInsight Pro. Real Estate Intelligence Platform for Modern Professionals</p>
            <p>Professional Property Analytics & Market Intelligence</p>
        </div>
    </footer>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <button class="modal-close" onclick="hideModals()">&times;</button>
            <h2 style="text-align: center; margin-bottom: 1.5rem;">Realtor Login</h2>
            
            <!-- Social Login Options -->
            <div class="social-login-section">
                <div class="social-login-buttons">
                    <button class="social-btn social-btn-google" onclick="loginWithGoogle()">
                        <svg width="20" height="20" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Continue with Google
                    </button>
                    
                    <button class="social-btn social-btn-microsoft" onclick="loginWithMicrosoft()">
                        <svg width="20" height="20" viewBox="0 0 24 24">
                            <path fill="#f25022" d="M1 1h10v10H1z"/>
                            <path fill="#00a4ef" d="M13 1h10v10H13z"/>
                            <path fill="#7fba00" d="M1 13h10v10H1z"/>
                            <path fill="#ffb900" d="M13 13h10v10H13z"/>
                        </svg>
                        Continue with Microsoft
                    </button>
                    
                    <button class="social-btn social-btn-linkedin" onclick="loginWithLinkedIn()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#0077b5">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                        Continue with LinkedIn
                    </button>
                </div>
                
                <div class="social-login-divider">
                    <span>or continue with email</span>
                </div>
            </div>
            
            <!-- Traditional Login Form -->
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" id="loginEmail" placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="loginPassword" placeholder="Enter your password">
            </div>
            <button class="btn-primary" style="width: 100%;" onclick="login()">Sign In</button>
            <p style="text-align: center; margin-top: 1rem;">
                <a href="#" onclick="hideModals(); showSignup();">Don't have an account? Sign up</a>
            </p>
            <div id="loginMessage"></div>
        </div>
    </div>

    <!-- Signup Modal -->
    <div id="signupModal" class="modal">
        <div class="modal-content">
            <button class="modal-close" onclick="hideModals()">&times;</button>
            <h2 style="text-align: center; margin-bottom: 1.5rem;">Create Realtor Account</h2>
            
            <!-- Social Signup Options -->
            <div class="social-login-section">
                <div class="social-login-buttons">
                    <button class="social-btn social-btn-google" onclick="signupWithGoogle()">
                        <svg width="20" height="20" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Sign up with Google
                    </button>
                    
                    <button class="social-btn social-btn-microsoft" onclick="signupWithMicrosoft()">
                        <svg width="20" height="20" viewBox="0 0 24 24">
                            <path fill="#f25022" d="M1 1h10v10H1z"/>
                            <path fill="#00a4ef" d="M13 1h10v10H13z"/>
                            <path fill="#7fba00" d="M1 13h10v10H1z"/>
                            <path fill="#ffb900" d="M13 13h10v10H13z"/>
                        </svg>
                        Sign up with Microsoft
                    </button>
                    
                    <button class="social-btn social-btn-linkedin" onclick="signupWithLinkedIn()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#0077b5">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                        Sign up with LinkedIn
                    </button>
                </div>
                
                <div class="social-login-divider">
                    <span>or sign up with email</span>
                </div>
            </div>
            
            <!-- Traditional Signup Form -->
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
            <button class="btn-primary" style="width: 100%;" onclick="signup()">Start Free Trial</button>
            <p style="text-align: center; margin-top: 1rem;">
                <a href="#" onclick="hideModals(); showLogin();">Already have an account? Sign in</a>
            </p>
            <div id="signupMessage"></div>
        </div>
    </div>

    <script>
        // Autocomplete functionality
        let autocompleteTimeout;
        let selectedIndex = -1;
        let currentSuggestions = [];

        // Initialize autocomplete for both search inputs
        document.addEventListener('DOMContentLoaded', function() {
            setupAutocomplete('heroLocation', 'heroAutocomplete');
            
            if (document.getElementById('location')) {
                setupAutocomplete('location', 'dashboardAutocomplete');
                
                // Check current search status
                fetch('/api/search-status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.searches_remaining !== undefined) {
                            updateSearchBanner(data.searches_remaining);
                        }
                    })
                    .catch(err => console.log('Could not check search status'));
                
                searchProperties();
            }
        });

        function setupAutocomplete(inputId, dropdownId) {
            const input = document.getElementById(inputId);
            const dropdown = document.getElementById(dropdownId);
            
            if (!input || !dropdown) return;

            input.addEventListener('input', function() {
                const query = this.value.trim();
                
                clearTimeout(autocompleteTimeout);
                
                if (query.length < 3) {
                    hideDropdown(dropdownId);
                    return;
                }

                autocompleteTimeout = setTimeout(() => {
                    searchAddresses(query, dropdownId, inputId);
                }, 300);
            });

            input.addEventListener('keydown', function(e) {
                const dropdown = document.getElementById(dropdownId);
                const items = dropdown.querySelectorAll('.autocomplete-item');
                
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                    updateSelection(dropdownId);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    selectedIndex = Math.max(selectedIndex - 1, -1);
                    updateSelection(dropdownId);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (selectedIndex >= 0 && items[selectedIndex]) {
                        selectAddress(inputId, dropdownId, currentSuggestions[selectedIndex]);
                    } else {
                        // Trigger search if no suggestion selected
                        if (inputId === 'heroLocation') {
                            heroSearch();
                        } else {
                            searchProperties();
                        }
                    }
                } else if (e.key === 'Escape') {
                    hideDropdown(dropdownId);
                }
            });

            // Hide dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                    hideDropdown(dropdownId);
                }
            });
        }

        async function searchAddresses(query, dropdownId, inputId) {
            try {
                // Using Nominatim (OpenStreetMap) for real address suggestions
                const response = await fetch(
                    `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=8&q=${encodeURIComponent(query)}&countrycodes=us`
                );
                
                if (response.ok) {
                    const data = await response.json();
                    showSuggestions(data, dropdownId, inputId);
                }
            } catch (error) {
                console.log('Autocomplete error:', error);
                // Fallback to basic suggestions if API fails
                showBasicSuggestions(query, dropdownId, inputId);
            }
        }

        function showSuggestions(data, dropdownId, inputId) {
            const dropdown = document.getElementById(dropdownId);
            currentSuggestions = data;
            selectedIndex = -1;
            
            if (data.length === 0) {
                hideDropdown(dropdownId);
                return;
            }

            let html = '';
            data.forEach((item, index) => {
                const displayName = item.display_name;
                const parts = displayName.split(',');
                const main = parts[0];
                const secondary = parts.slice(1, 3).join(',');
                
                html += `
                    <div class="autocomplete-item" onclick="selectAddressFromList(${index}, '${inputId}', '${dropdownId}')">
                        <div class="autocomplete-main">${main}</div>
                        <div class="autocomplete-secondary">${secondary}</div>
                    </div>
                `;
            });
            
            dropdown.innerHTML = html;
            dropdown.classList.add('show');
        }

        function showBasicSuggestions(query, dropdownId, inputId) {
            const dropdown = document.getElementById(dropdownId);
            
            // Basic US city suggestions if API fails
            const basicSuggestions = [
                { display_name: `${query}, Florida, United States` },
                { display_name: `${query}, Texas, United States` },
                { display_name: `${query}, California, United States` },
                { display_name: `${query}, New York, United States` }
            ];
            
            currentSuggestions = basicSuggestions;
            selectedIndex = -1;
            
            let html = '';
            basicSuggestions.forEach((item, index) => {
                html += `
                    <div class="autocomplete-item" onclick="selectAddressFromList(${index}, '${inputId}', '${dropdownId}')">
                        <div class="autocomplete-main">${item.display_name}</div>
                    </div>
                `;
            });
            
            dropdown.innerHTML = html;
            dropdown.classList.add('show');
        }

        function updateSelection(dropdownId) {
            const dropdown = document.getElementById(dropdownId);
            const items = dropdown.querySelectorAll('.autocomplete-item');
            
            items.forEach((item, index) => {
                if (index === selectedIndex) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        function selectAddressFromList(index, inputId, dropdownId) {
            if (currentSuggestions[index]) {
                selectAddress(inputId, dropdownId, currentSuggestions[index]);
            }
        }

        function selectAddress(inputId, dropdownId, suggestion) {
            const input = document.getElementById(inputId);
            const displayName = suggestion.display_name;
            
            // Extract city and state from the suggestion
            const parts = displayName.split(',');
            let formattedAddress = parts[0];
            
            // Try to get city, state format
            if (parts.length >= 2) {
                const city = parts[0].trim();
                const state = parts[1].trim();
                formattedAddress = `${city}, ${state}`;
            }
            
            input.value = formattedAddress;
            hideDropdown(dropdownId);
            
            // Auto-trigger search after selection
            setTimeout(() => {
                if (inputId === 'heroLocation') {
                    heroSearch();
                } else {
                    searchProperties();
                }
            }, 100);
        }

        function hideDropdown(dropdownId) {
            const dropdown = document.getElementById(dropdownId);
            dropdown.classList.remove('show');
            selectedIndex = -1;
            currentSuggestions = [];
        }

        // Mobile Menu Functions
        function toggleMobileMenu() {
            const mobileNav = document.getElementById('mobileNav');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            mobileNav.classList.toggle('active');
            toggle.classList.toggle('active');
        }

        function closeMobileMenu() {
            const mobileNav = document.getElementById('mobileNav');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            mobileNav.classList.remove('active');
            toggle.classList.remove('active');
        }

        // Navigation Functions
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Remove active class from all nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageId).classList.add('active');
            
            // Add active class to clicked nav link
            event.target.classList.add('active');
        }

        // Modal Functions
        function showLogin() {
            hideModals();
            document.getElementById('loginModal').style.display = 'block';
        }

        function showSignup() {
            hideModals();
            document.getElementById('signupModal').style.display = 'block';
        }

        function hideModals() {
            document.getElementById('loginModal').style.display = 'none';
            document.getElementById('signupModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                hideModals();
            }
            
            // Close mobile menu when clicking outside
            if (!event.target.closest('.navbar') && !event.target.closest('.mobile-nav')) {
                closeMobileMenu();
            }
        }

        // Hero Search (Free Trial)
        async function heroSearch() {
            const location = document.getElementById('heroLocation').value;
            if (!location) {
                alert('Please enter a location');
                return;
            }

            try {
                const response = await fetch('/api/hero-search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location })
                });

                if (response.ok) {
                    const data = await response.json();
                    displayHeroResults(data);
                } else {
                    alert('Search failed. Please try again.');
                }
            } catch (err) {
                alert('Network error: ' + err.message);
            }
        }

        function displayHeroResults(data) {
            const results = document.getElementById('heroSearchResults');
            const properties = data.properties || [];
            
            if (properties.length === 0) {
                results.innerHTML = '<div class="hero-property-card">No properties found for this location.</div>';
                return;
            }

            let html = '<h4 style="color: white; margin-bottom: 1rem;">Found ' + Math.min(properties.length, 2) + ' sample properties:</h4>';
            
            // Show only first 2 properties for free search
            properties.slice(0, 2).forEach(prop => {
                html += '<div class="hero-property-card">';
                html += '<strong>' + (prop.address || 'Address not available') + '</strong><br>';
                html += 'Type: ' + (prop.property_type || 'N/A') + ' | ';
                html += 'Bedrooms: ' + (prop.bedrooms || 'N/A') + ' | ';
                html += 'Bathrooms: ' + (prop.bathrooms || 'N/A') + '<br>';
                html += 'Rent Estimate: ' + (prop.rent_estimate || 'N/A');
                html += '</div>';
            });
            
            html += '<div style="text-align: center; margin-top: 1rem;">';
            html += '<p style="color: white; margin-bottom: 1rem;">Want to see all ' + properties.length + ' properties and get detailed analytics?</p>';
            html += '<button class="btn-primary" onclick="showSignup()">Sign Up for 5 Free Searches</button>';
            html += '</div>';
            
            results.innerHTML = html;
        }
        async function signup() {
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const license = document.getElementById('signupLicense').value;
            const password = document.getElementById('signupPassword').value;

            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, license, password })
                });

                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const error = await response.json();
                    document.getElementById('signupMessage').innerHTML = '<div style="color: red; margin-top: 1rem;">' + error.message + '</div>';
                }
            } catch (err) {
                document.getElementById('signupMessage').innerHTML = '<div style="color: red; margin-top: 1rem;">Signup failed: ' + err.message + '</div>';
            }
        }

        async function login() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const error = await response.json();
                    document.getElementById('loginMessage').innerHTML = '<div style="color: red; margin-top: 1rem;">' + error.message + '</div>';
                }
            } catch (err) {
                document.getElementById('loginMessage').innerHTML = '<div style="color: red; margin-top: 1rem;">Login failed: ' + err.message + '</div>';
            }
        }
    </script>
</body>
</html>
'''

# Dashboard Template (for logged-in users)
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - PropInsight Pro</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 2rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        .logout-btn {
            background: #e53e3e;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
        }
        .search-section {
            background: #f8fafc;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .search-form {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .search-input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
        }
        .search-wrapper-dashboard {
            position: relative;
            flex: 1;
        }
        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            z-index: 1000;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            margin-top: 5px;
        }
        .autocomplete-dropdown.show { display: block; }
        .autocomplete-item {
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s ease;
            color: #333;
        }
        .autocomplete-item:hover, .autocomplete-item.selected {
            background-color: #f8f9fa;
        }
        .autocomplete-main {
            font-weight: 600;
            margin-bottom: 2px;
        }
        .autocomplete-secondary {
            font-size: 0.85em;
            color: #666;
        }
        .search-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
        }
        .property-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        .property-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .property-address {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .error { color: red; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>PropInsight Pro Dashboard</h1>
            <div>
                <span>Welcome, {{ session.realtor_name }}! ({{ session.license }})</span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>

        <div class="search-section">
            <h2>Property Search</h2>
            <div id="searchLimitBanner" class="trial-banner" style="display: none;"></div>
            <div class="search-form">
                <div class="search-wrapper-dashboard">
                    <input type="text" id="location" class="search-input" placeholder="Enter city or address (e.g., Orlando, FL)" value="Orlando, FL" autocomplete="off">
                    <div class="autocomplete-dropdown" id="dashboardAutocomplete"></div>
                </div>
                <button class="search-btn" onclick="searchProperties()">Search Properties</button>
            </div>
            <div id="upgradePrompt" style="display: none;"></div>
            <div id="results"></div>
            <div id="error" class="error" style="display: none;"></div>
        </div>
    </div>

    <script>
        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/';
        }

        async function searchProperties() {
            const location = document.getElementById('location').value;
            if (!location) return;

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.search_limit_reached) {
                        showUpgradePrompt();
                    } else {
                        displayResults(data);
                        updateSearchBanner(data.searches_remaining);
                    }
                } else {
                    const error = await response.json();
                    if (error.upgrade_required) {
                        showUpgradePrompt();
                    } else {
                        showError('Search failed');
                    }
                }
            } catch (err) {
                showError('Network error: ' + err.message);
            }
        }

        function updateSearchBanner(remaining) {
            const banner = document.getElementById('searchLimitBanner');
            if (remaining !== undefined && remaining >= 0) {
                banner.style.display = 'block';
                if (remaining > 0) {
                    banner.innerHTML = `Free Trial: ${remaining} searches remaining. <a href="#" onclick="showPage('pricing')" style="color: white; text-decoration: underline;">Upgrade for unlimited searches</a>`;
                    banner.style.background = 'linear-gradient(45deg, #48bb78, #38a169)';
                } else {
                    banner.innerHTML = 'Free trial used up. Upgrade to continue searching!';
                    banner.style.background = 'linear-gradient(45deg, #ed8936, #dd6b20)';
                }
            }
        }

        function showUpgradePrompt() {
            const prompt = document.getElementById('upgradePrompt');
            prompt.style.display = 'block';
            prompt.innerHTML = `
                <div class="upgrade-prompt">
                    <h3>Free Searches Used Up!</h3>
                    <p>You've used all your free searches. Upgrade to continue searching properties and unlock all features.</p>
                    <button onclick="showPage('pricing')">View Pricing Plans</button>
                    <button onclick="showSignup()">Upgrade Now</button>
                </div>
            `;
            document.getElementById('results').innerHTML = '';
        }

        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.style.display = 'block';
        }

        function displayResults(data) {
            const results = document.getElementById('results');
            const properties = data.properties || [];
            
            if (properties.length === 0) {
                results.innerHTML = '<p>No properties found.</p>';
                return;
            }

            let html = '<h3>Found ' + properties.length + ' properties:</h3>';
            html += '<div class="property-grid">';
            
            properties.forEach(prop => {
                html += '<div class="property-card">';
                html += '<div class="property-address">' + (prop.address || 'Address not available') + '</div>';
                html += '<p><strong>Type:</strong> ' + (prop.property_type || 'N/A') + '</p>';
                html += '<p><strong>Bedrooms:</strong> ' + (prop.bedrooms || 'N/A') + '</p>';
                html += '<p><strong>Bathrooms:</strong> ' + (prop.bathrooms || 'N/A') + '</p>';
                html += '<p><strong>Square Feet:</strong> ' + (prop.square_feet || 'N/A') + '</p>';
                html += '<p><strong>Rent Estimate:</strong> ' + (prop.rent_estimate || 'N/A') + '</p>';
                html += '</div>';
            });
            
            html += '</div>';
            results.innerHTML = html;
            document.getElementById('error').style.display = 'none';
        }

        // Auto-search on page load and check limits
        document.addEventListener('DOMContentLoaded', function() {
            if (document.getElementById('location')) {
                // Setup autocomplete for dashboard
                setupAutocomplete('location', 'dashboardAutocomplete');
                
                // Check current search status
                fetch('/api/search-status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.searches_remaining !== undefined) {
                            updateSearchBanner(data.searches_remaining);
                        }
                    })
                    .catch(err => console.log('Could not check search status'));
                
                searchProperties();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, page_title="Home")

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
        'password_hash': password_hash
    }
    
    session['user_id'] = user_id
    session['realtor_name'] = name
    session['license'] = license_num
    session['email'] = email
    
    print(f"New realtor signed up: {name} ({email}) - License: {license_num}")
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
    
    print(f"Realtor logged in: {user['name']} ({email})")
    return jsonify({'status': 'success'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})

# OAuth Routes (for future implementation)
@app.route('/auth/google')
def google_auth():
    """
    Google OAuth endpoint - In production, this would:
    1. Redirect to Google OAuth consent screen
    2. Handle the callback with authorization code
    3. Exchange code for access token
    4. Get user profile information
    5. Create or login user account
    """
    return jsonify({'message': 'Google OAuth integration coming soon'}), 501

@app.route('/auth/microsoft')
def microsoft_auth():
    """Microsoft OAuth endpoint"""
    return jsonify({'message': 'Microsoft OAuth integration coming soon'}), 501

@app.route('/auth/linkedin')
def linkedin_auth():
    """LinkedIn OAuth endpoint"""
    return jsonify({'message': 'LinkedIn OAuth integration coming soon'}), 501

@app.route('/auth/callback/<provider>')
def oauth_callback(provider):
    """
    OAuth callback handler for all providers
    In production, this would:
    1. Receive authorization code from OAuth provider
    2. Exchange for access token
    3. Get user profile
    4. Create session
    5. Redirect to dashboard
    """
    return jsonify({'message': f'{provider} OAuth callback coming soon'}), 501

@app.route('/api/search-status', methods=['GET'])
def search_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if 'search_count' not in session:
        session['search_count'] = 0
    
    searches_remaining = 5 - session['search_count']
    
    return jsonify({
        'search_count': session['search_count'],
        'searches_remaining': searches_remaining,
        'trial_active': searches_remaining > 0
    })

@app.route('/api/hero-search', methods=['POST'])
def hero_search():
    """Free search for visitors (no login required)"""
    try:
        data = request.get_json()
        location = data.get('location', '').strip()
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Parse location
        parts = [p.strip() for p in location.split(',')]
        city = parts[0]
        state = parts[1] if len(parts) > 1 else 'FL'
        
        print(f"Hero search: {city}, {state}")
        
        # Try to import services
        try:
            from app.services.property_service import PropertyService
            property_service = PropertyService()
            properties = property_service.search_properties(city, state, limit=5)
            data_source = "RentCast API"
        except Exception as e:
            print(f"Service import failed: {str(e)}")
            # More realistic fallback data based on actual location
            properties = _get_realistic_fallback_data(city, state)
            data_source = "Sample Data"
        
        result = {
            'properties': properties,
            'search_info': {
                'location': f"{city}, {state}",
                'properties_found': len(properties),
                'data_source': data_source,
                'search_type': 'free_trial'
            }
        }
        
        print(f"Hero search returning {len(properties)} properties")
        return jsonify(result)
        
    except Exception as e:
        print(f"Hero search error: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

def _get_realistic_fallback_data(city, state, limit=5):
    """Generate realistic property data based on actual location"""
    import random
    
    # Real street name patterns by region
    street_patterns = {
        'FL': ['Ocean View Dr', 'Palm Beach Blvd', 'Sunset Way', 'Orange Grove St', 'Marina Dr', 'Bayfront Ave', 'Gulf Shore Dr'],
        'TX': ['Ranch Road', 'Bluebonnet Dr', 'Mockingbird Ln', 'Live Oak St', 'Pecan Grove Dr', 'Hill Country Dr', 'Lone Star Ave'],
        'CA': ['Pacific Coast Hwy', 'Redwood Dr', 'Golden Gate Ave', 'Sunset Blvd', 'Ocean View Dr', 'Hillside Dr', 'Valley View St'],
        'NY': ['Madison Ave', 'Park Place', 'Broadway St', 'Riverside Dr', 'Central Park West', 'Fifth Avenue', 'Wall Street'],
        'DEFAULT': ['Main Street', 'Oak Avenue', 'Maple Drive', 'Pine Road', 'Cedar Lane', 'Elm Street', 'Park Avenue']
    }
    
    # Property types by region
    property_types = {
        'FL': ['Condo', 'Single Family', 'Townhouse', 'Apartment'],
        'TX': ['Single Family', 'Ranch', 'Townhouse', 'Apartment'],
        'CA': ['Single Family', 'Condo', 'Apartment', 'Townhouse'],
        'DEFAULT': ['Single Family', 'Apartment', 'Condo', 'Townhouse']
    }
    
    # Price ranges by state (rough estimates)
    price_ranges = {
        'FL': (1800, 3500),
        'TX': (1500, 3000),
        'CA': (2500, 5000),
        'NY': (2000, 4500),
        'DEFAULT': (1200, 2800)
    }
    
    streets = street_patterns.get(state, street_patterns['DEFAULT'])
    prop_types = property_types.get(state, property_types['DEFAULT'])
    price_min, price_max = price_ranges.get(state, price_ranges['DEFAULT'])
    
    properties = []
    
    for i in range(limit):
        # Generate realistic address
        house_num = random.randint(100, 9999)
        street = random.choice(streets)
        
        # Generate realistic property details
        prop_type = random.choice(prop_types)
        bedrooms = random.choice([1, 2, 2, 3, 3, 3, 4, 4, 5])
        bathrooms = random.choice([1, 1.5, 2, 2.5, 3, 3.5])
        
        # Square footage based on bedrooms
        base_sqft = bedrooms * 350 + random.randint(200, 500)
        square_feet = base_sqft + random.randint(-200, 300)
        
        # Year built
        year_built = random.randint(1985, 2023)
        
        # Rent estimate based on local market and property size
        base_rent = random.randint(price_min, price_max)
        
        # Adjust rent based on property characteristics
        if prop_type == 'Single Family':
            base_rent *= random.uniform(1.2, 1.5)
        elif prop_type == 'Condo':
            base_rent *= random.uniform(1.1, 1.3)
        
        # Adjust for bedrooms
        bedroom_multiplier = {1: 0.7, 2: 1.0, 3: 1.3, 4: 1.6, 5: 2.0}
        base_rent *= bedroom_multiplier.get(bedrooms, 1.0)
        
        # Random variation
        final_rent = int(base_rent * random.uniform(0.9, 1.1))
        
        property_data = {
            'address': f'{house_num} {street}, {city}, {state}',
            'property_type': prop_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'square_feet': square_feet,
            'year_built': year_built,
            'rent_estimate': f'${final_rent:,}',
            'county': f'{city} County',
            'zip_code': f'{random.randint(10000, 99999)}'
        }
        
        properties.append(property_data)
    
    return properties

@app.route('/api/search', methods=['POST'])
def search_properties():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Initialize search count if not exists
        if 'search_count' not in session:
            session['search_count'] = 0
        
        # Check if user has exceeded free trial (5 searches)
        if session['search_count'] >= 5:
            return jsonify({
                'error': 'Free trial limit reached',
                'upgrade_required': True,
                'message': 'You have used all 5 free searches. Please upgrade to continue.'
            }), 403
        
        data = request.get_json()
        location = data.get('location', '').strip()
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Parse location
        parts = [p.strip() for p in location.split(',')]
        city = parts[0]
        state = parts[1] if len(parts) > 1 else 'FL'
        
        print(f"Search by {session['realtor_name']}: {city}, {state} (Search #{session['search_count'] + 1})")
        
        # Try to import services
        try:
            from app.services.property_service import PropertyService
            property_service = PropertyService()
            properties = property_service.search_properties(city, state, limit=10)
            data_source = "RentCast API"
        except Exception as e:
            print(f"Service import failed: {str(e)}")
            # More realistic fallback data
            properties = _get_realistic_fallback_data(city, state, 5)
            data_source = "Sample Data"
        
        # Increment search count
        session['search_count'] += 1
        searches_remaining = 5 - session['search_count']
        
        result = {
            'properties': properties,
            'search_info': {
                'location': f"{city}, {state}",
                'properties_found': len(properties),
                'data_source': data_source,
                'realtor': session['realtor_name']
            },
            'searches_remaining': searches_remaining,
            'search_count': session['search_count']
        }
        
        print(f"Returning {len(properties)} properties, {searches_remaining} searches remaining")
        return jsonify(result)
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting PropInsight Pro - Real Estate Intelligence Platform...")
    print("Open: http://localhost:5001")
    print("Features: Professional marketing site with freemium model")
    app.run(host='0.0.0.0', port=5001, debug=True)