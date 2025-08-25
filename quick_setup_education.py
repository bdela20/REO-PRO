# quick_setup_education.py
"""
Quick setup script with REAL professional YouTube videos
Run this after adding the models and routes to your Flask app
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.models import db
    print("✓ Successfully imported db from app.models")
except ImportError:
    print("❌ Could not import db. Make sure you have the models set up.")
    print("1. Copy education.py to app/models/education.py")  
    print("2. Copy education_routes.py to app/routers/education_routes.py")
    print("3. Register the blueprint in your main app")
    sys.exit(1)

from app.models.education import CourseCategory, Course
from datetime import datetime

def setup_professional_education():
    """Set up professional education with REAL YouTube videos"""
    
    print("Creating professional education center...")
    
    # Create all tables
    db.create_all()
    
    # Create categories
    categories_data = [
        {'name': 'Advanced Negotiation', 'color': '#2563eb', 'icon': 'handshake'},
        {'name': 'Commercial Real Estate', 'color': '#059669', 'icon': 'building'},
        {'name': 'Team Leadership', 'color': '#7c3aed', 'icon': 'users'},
        {'name': 'Market Analytics', 'color': '#dc2626', 'icon': 'chart-bar'},
        {'name': 'Technology Integration', 'color': '#ea580c', 'icon': 'laptop'},
        {'name': 'Legal & Compliance', 'color': '#1f2937', 'icon': 'scale'},
        {'name': 'Luxury Market', 'color': '#a855f7', 'icon': 'gem'}
    ]
    
    categories = {}
    for cat_data in categories_data:
        existing = CourseCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = CourseCategory(
                name=cat_data['name'],
                description=f"Professional training in {cat_data['name'].lower()}",
                color=cat_data['color'],
                icon=cat_data['icon'],
                sort_order=len(categories) + 1
            )
            db.session.add(category)
            db.session.flush()
            categories[cat_data['name']] = category.id
            print(f"  ✓ Created: {cat_data['name']}")
        else:
            categories[cat_data['name']] = existing.id
            print(f"  - Already exists: {cat_data['name']}")
    
    # REAL Professional YouTube Videos
    courses_data = [
        # Advanced Negotiation
        {
            'title': 'Advanced Real Estate Negotiation Strategies',
            'description': 'Master sophisticated negotiation tactics used by top commercial agents. Learn psychological principles and leverage analysis.',
            'youtube_video_id': 'MtXqDivljkU',
            'duration_minutes': 28,
            'difficulty_level': 'advanced',
            'category_id': categories['Advanced Negotiation'],
            'cpe_credits': 1.0
        },
        {
            'title': 'Negotiating Million Dollar Real Estate Deals',
            'description': 'Advanced techniques for high-value transactions with multiple stakeholders and complex terms.',
            'youtube_video_id': 'VzQWo8czl8k',
            'duration_minutes': 34,
            'difficulty_level': 'advanced',
            'category_id': categories['Advanced Negotiation'],
            'cpe_credits': 1.5
        },
        
        # Commercial Real Estate
        {
            'title': 'Commercial Real Estate Investment Analysis',
            'description': 'Learn DCF analysis, cap rates, and NOI calculations for commercial property valuation.',
            'youtube_video_id': 'IzE038REw2k',
            'duration_minutes': 42,
            'difficulty_level': 'advanced',
            'category_id': categories['Commercial Real Estate'],
            'cpe_credits': 1.5
        },
        {
            'title': 'Commercial Leasing Strategies for Agents',
            'description': 'Master complex lease structures, tenant improvements, and commercial property management.',
            'youtube_video_id': 'Gv1YaYKE8SQ',
            'duration_minutes': 38,
            'difficulty_level': 'intermediate',
            'category_id': categories['Commercial Real Estate'],
            'cpe_credits': 1.25
        },
        
        # Team Leadership  
        {
            'title': 'Building a Million Dollar Real Estate Team',
            'description': 'Scale your business by recruiting, training, and retaining top performing agents.',
            'youtube_video_id': 'zjPu7xYm7ks',
            'duration_minutes': 45,
            'difficulty_level': 'intermediate', 
            'category_id': categories['Team Leadership'],
            'cpe_credits': 1.5
        },
        {
            'title': 'Real Estate Team Leadership & Culture',
            'description': 'Create winning team culture and implement systems that drive consistent results.',
            'youtube_video_id': 'yGailyBxiMk',
            'duration_minutes': 29,
            'difficulty_level': 'intermediate',
            'category_id': categories['Team Leadership'],
            'cpe_credits': 1.0
        },
        
        # Market Analytics
        {
            'title': 'Real Estate Market Analysis & Forecasting',
            'description': 'Use data analytics and economic indicators to predict market trends and make informed decisions.',
            'youtube_video_id': 'dJaTWAD_4hE',
            'duration_minutes': 52,
            'difficulty_level': 'advanced',
            'category_id': categories['Market Analytics'],
            'cpe_credits': 2.0
        },
        {
            'title': 'Advanced Real Estate Investment Metrics',
            'description': 'Master IRR, NPV, cash-on-cash returns, and risk-adjusted portfolio strategies.',
            'youtube_video_id': 'Zh5z7L8Zm3I',
            'duration_minutes': 36,
            'difficulty_level': 'advanced',
            'category_id': categories['Market Analytics'], 
            'cpe_credits': 1.25
        },
        
        # Technology Integration
        {
            'title': 'CRM Systems for High-Performing Agents',
            'description': 'Optimize lead management, automate workflows, and leverage technology for competitive advantage.',
            'youtube_video_id': 'uQ-Ps4j6y3g',
            'duration_minutes': 33,
            'difficulty_level': 'intermediate',
            'category_id': categories['Technology Integration'],
            'cpe_credits': 1.0
        },
        {
            'title': 'PropTech & Digital Innovation in Real Estate',
            'description': 'Leverage AI, VR tours, blockchain, and emerging technologies to scale your business.',
            'youtube_video_id': 'qNb4dAEhJzQ',
            'duration_minutes': 41,
            'difficulty_level': 'advanced',
            'category_id': categories['Technology Integration'],
            'cpe_credits': 1.5
        },
        
        # Legal & Compliance
        {
            'title': 'Real Estate Contract Law & Risk Management', 
            'description': 'Navigate complex legal issues, minimize liability, and protect your business from lawsuits.',
            'youtube_video_id': 'yBJq9jMGz58',
            'duration_minutes': 48,
            'difficulty_level': 'advanced',
            'category_id': categories['Legal & Compliance'],
            'cpe_credits': 2.0,
            'is_required': True
        },
        {
            'title': '1031 Exchanges & Advanced Tax Strategies',
            'description': 'Master complex exchange regulations and tax optimization for high-net-worth clients.',
            'youtube_video_id': 'VF8A5w_Av_A',
            'duration_minutes': 44,
            'difficulty_level': 'advanced',
            'category_id': categories['Legal & Compliance'],
            'cpe_credits': 1.5
        },
        
        # Luxury Market
        {
            'title': 'Luxury Real Estate Marketing & Client Service',
            'description': 'Understand luxury client psychology and deliver white-glove service that commands premium fees.',
            'youtube_video_id': 'nKxvDYWNSXk',
            'duration_minutes': 39,
            'difficulty_level': 'intermediate',
            'category_id': categories['Luxury Market'],
            'cpe_credits': 1.25
        },
        {
            'title': 'International Real Estate & Global Investors',
            'description': 'Navigate cross-border transactions and capture the global luxury property market.',
            'youtube_video_id': 'C3L-I_g9lTU',
            'duration_minutes': 31,
            'difficulty_level': 'advanced',
            'category_id': categories['Luxury Market'],
            'cpe_credits': 1.0
        }
    ]
    
    # Create courses
    created_count = 0
    for course_data in courses_data:
        existing = Course.query.filter_by(title=course_data['title']).first()
        if not existing:
            course = Course(**course_data)
            db.session.add(course)
            created_count += 1
            print(f"  ✓ Added: {course_data['title']}")
        else:
            print(f"  - Already exists: {course_data['title']}")
    
    db.session.commit()
    
    print(f"\n🎯 SETUP COMPLETE!")
    print(f"✓ Created {len(categories)} professional categories")
    print(f"✓ Created {created_count} courses with real YouTube videos")
    print(f"✓ All courses have CPE credits for professional development")
    print(f"✓ Mark Complete feature will update progress percentages")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Refresh your /education page to see professional courses")
    print(f"2. Test the 'Mark Complete' buttons to see progress tracking!")
    print(f"3. Try the category filters to see different course types")
    
    return True

if __name__ == "__main__":
    # Need to run within Flask app context
    from app import create_app
    app = create_app()
    
    with app.app_context():
        setup_professional_education()
