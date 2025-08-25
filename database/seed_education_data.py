# database/seed_education_data.py
"""
Professional Education Center Seed Data
Creates categories and courses that will impress brokerages and big companies
"""

from app import create_app, db
from app.models.education import CourseCategory, Course
from datetime import datetime

def create_professional_categories():
    """Create professional course categories for experienced realtors"""
    categories = [
        {
            'name': 'Advanced Negotiation',
            'description': 'Master complex negotiation strategies for high-value transactions',
            'color': '#2563eb',
            'icon': 'handshake',
            'sort_order': 1
        },
        {
            'name': 'Commercial Real Estate',
            'description': 'Commercial property analysis, leasing, and investment strategies',
            'color': '#059669',
            'icon': 'building',
            'sort_order': 2
        },
        {
            'name': 'Team Leadership',
            'description': 'Build and manage successful real estate teams',
            'color': '#7c3aed',
            'icon': 'users',
            'sort_order': 3
        },
        {
            'name': 'Market Analytics',
            'description': 'Advanced market analysis and data-driven decision making',
            'color': '#dc2626',
            'icon': 'chart-bar',
            'sort_order': 4
        },
        {
            'name': 'Technology Integration',
            'description': 'Leverage technology for competitive advantage',
            'color': '#ea580c',
            'icon': 'laptop',
            'sort_order': 5
        },
        {
            'name': 'Legal & Compliance',
            'description': 'Stay compliant and protect your business from liability',
            'color': '#1f2937',
            'icon': 'scale',
            'sort_order': 6
        },
        {
            'name': 'Luxury Market',
            'description': 'Strategies for high-end property sales and luxury client service',
            'color': '#a855f7',
            'icon': 'gem',
            'sort_order': 7
        }
    ]
    
    created_categories = {}
    for cat_data in categories:
        # Check if category already exists
        existing = CourseCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = CourseCategory(**cat_data)
            db.session.add(category)
            db.session.flush()  # Get ID without committing
            created_categories[cat_data['name']] = category.id
        else:
            created_categories[cat_data['name']] = existing.id
    
    db.session.commit()
    return created_categories

def create_professional_courses(categories):
    """Create professional-level courses that will impress brokerages"""
    
    courses = [
        # Advanced Negotiation
        {
            'title': 'Advanced Commercial Negotiation Strategies',
            'description': 'Master sophisticated negotiation tactics used in million-dollar commercial transactions. Learn psychological principles, leverage analysis, and creative deal structuring.',
            'youtube_video_id': 'VzQWo8czl8k',  # Professional negotiation content
            'duration_minutes': 45,
            'difficulty_level': 'advanced',
            'category_id': categories['Advanced Negotiation'],
            'cpe_credits': 1.5,
            'is_required': False
        },
        {
            'title': 'Multi-Party Negotiation Mastery',
            'description': 'Navigate complex deals involving multiple stakeholders, attorneys, and decision-makers. Advanced tactics for closing challenging transactions.',
            'youtube_video_id': '6JCcLUT-ykQ',  # Multi-party negotiation
            'duration_minutes': 52,
            'difficulty_level': 'advanced',
            'category_id': categories['Advanced Negotiation'],
            'cpe_credits': 1.75,
            'is_required': False
        },
        
        # Commercial Real Estate
        {
            'title': 'Commercial Property Valuation & Analysis',
            'description': 'Advanced techniques for valuing commercial properties, including DCF analysis, cap rate determination, and market comparables for office, retail, and industrial properties.',
            'youtube_video_id': 'Gv1YaYKE8SQ',  # Commercial valuation
            'duration_minutes': 38,
            'difficulty_level': 'intermediate',
            'category_id': categories['Commercial Real Estate'],
            'cpe_credits': 1.25,
            'is_required': False
        },
        {
            'title': 'Commercial Lease Structure & Negotiations',
            'description': 'Master complex lease negotiations including NNN leases, percentage rents, tenant improvements, and lease renewals for commercial properties.',
            'youtube_video_id': 'kHXK6AhO9KM',  # Commercial leasing
            'duration_minutes': 43,
            'difficulty_level': 'advanced',
            'category_id': categories['Commercial Real Estate'],
            'cpe_credits': 1.5,
            'is_required': False
        },
        
        # Team Leadership
        {
            'title': 'Building High-Performance Real Estate Teams',
            'description': 'Recruit, train, and retain top talent. Create compensation structures, establish accountability systems, and scale your team effectively.',
            'youtube_video_id': 'zjPu7xYm7ks',  # Team leadership
            'duration_minutes': 36,
            'difficulty_level': 'intermediate',
            'category_id': categories['Team Leadership'],
            'cpe_credits': 1.0,
            'is_required': False
        },
        {
            'title': 'Real Estate Team Culture & Systems',
            'description': 'Develop winning team culture, implement scalable systems, and create processes that drive consistent results across your organization.',
            'youtube_video_id': 'Ap5DjO8Hftg',  # Team systems
            'duration_minutes': 41,
            'difficulty_level': 'advanced',
            'category_id': categories['Team Leadership'],
            'cpe_credits': 1.25,
            'is_required': False
        },
        
        # Market Analytics
        {
            'title': 'Advanced Market Analysis & Forecasting',
            'description': 'Use statistical models, economic indicators, and data analytics to predict market trends and make informed investment decisions.',
            'youtube_video_id': 'dJaTWAD_4hE',  # Market analysis
            'duration_minutes': 47,
            'difficulty_level': 'advanced',
            'category_id': categories['Market Analytics'],
            'cpe_credits': 1.5,
            'is_required': False
        },
        {
            'title': 'Real Estate Investment Analysis & Metrics',
            'description': 'Master IRR, NPV, cash-on-cash returns, and other investment metrics. Analyze risk-adjusted returns and portfolio optimization strategies.',
            'youtube_video_id': 'IzE038REw2k',  # Investment analysis
            'duration_minutes': 39,
            'difficulty_level': 'advanced',
            'category_id': categories['Market Analytics'],
            'cpe_credits': 1.25,
            'is_required': False
        },
        
        # Technology Integration
        {
            'title': 'CRM Automation & Lead Management Systems',
            'description': 'Optimize your CRM for maximum efficiency. Set up automated workflows, lead scoring, and nurture campaigns that convert prospects into clients.',
            'youtube_video_id': 'uQ-Ps4j6y3g',  # CRM systems
            'duration_minutes': 33,
            'difficulty_level': 'intermediate',
            'category_id': categories['Technology Integration'],
            'cpe_credits': 1.0,
            'is_required': False
        },
        {
            'title': 'PropTech Integration for Competitive Advantage',
            'description': 'Leverage cutting-edge property technology including AI, VR tours, blockchain, and IoT to differentiate your services and increase efficiency.',
            'youtube_video_id': 'qNb4dAEhJzQ',  # PropTech
            'duration_minutes': 44,
            'difficulty_level': 'advanced',
            'category_id': categories['Technology Integration'],
            'cpe_credits': 1.5,
            'is_required': False
        },
        
        # Legal & Compliance
        {
            'title': 'Advanced Contract Law & Risk Mitigation',
            'description': 'Navigate complex legal issues, understand liability exposure, and structure deals to minimize legal risks while maximizing protection.',
            'youtube_video_id': 'yBJq9jMGz58',  # Contract law
            'duration_minutes': 49,
            'difficulty_level': 'advanced',
            'category_id': categories['Legal & Compliance'],
            'cpe_credits': 2.0,
            'is_required': True  # Important for liability protection
        },
        {
            'title': '1031 Exchanges & Tax Strategy Optimization',
            'description': 'Master complex 1031 exchange regulations, timing requirements, and tax optimization strategies for high-net-worth clients.',
            'youtube_video_id': 'VF8A5w_Av_A',  # 1031 exchanges
            'duration_minutes': 37,
            'difficulty_level': 'advanced',
            'category_id': categories['Legal & Compliance'],
            'cpe_credits': 1.25,
            'is_required': False
        },
        
        # Luxury Market
        {
            'title': 'Luxury Client Psychology & Service Excellence',
            'description': 'Understand the mindset of ultra-high-net-worth clients. Deliver white-glove service that justifies premium commissions.',
            'youtube_video_id': 'nKxvDYWNSXk',  # Luxury service
            'duration_minutes': 42,
            'difficulty_level': 'intermediate',
            'category_id': categories['Luxury Market'],
            'cpe_credits': 1.25,
            'is_required': False
        },
        {
            'title': 'International Real Estate & Global Buyers',
            'description': 'Navigate international transactions, understand foreign buyer regulations, and capture the global luxury market opportunity.',
            'youtube_video_id': 'Zh5z7L8Zm3I',  # International real estate
            'duration_minutes': 35,
            'difficulty_level': 'advanced',
            'category_id': categories['Luxury Market'],
            'cpe_credits': 1.0,
            'is_required': False
        }
    ]
    
    created_courses = []
    for course_data in courses:
        # Check if course already exists
        existing = Course.query.filter_by(title=course_data['title']).first()
        if not existing:
            course = Course(**course_data)
            db.session.add(course)
            created_courses.append(course)
    
    db.session.commit()
    return created_courses

def setup_education_database():
    """Main function to set up the entire education system"""
    print("Setting up Professional Education Center...")
    
    # Create all tables
    print("Creating database tables...")
    db.create_all()
    
    # Create categories
    print("Creating professional course categories...")
    categories = create_professional_categories()
    print(f"Created {len(categories)} categories")
    
    # Create courses
    print("Creating professional courses...")
    courses = create_professional_courses(categories)
    print(f"Created {len(courses)} courses")
    
    print("Professional Education Center setup complete!")
    print("\nFeatures added:")
    print("- 7 professional categories targeting experienced realtors")
    print("- 14 advanced courses with CPE credits")
    print("- Progress tracking and completion system")
    print("- Analytics dashboard for brokerages")
    print("- User statistics and learning paths")
    
    return True

# Run setup script
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        setup_education_database()


# ============================================================================
# Migration Script (Alternative approach using Flask-Migrate)
# ============================================================================

def create_migration_sql():
    """Generate SQL for manual database setup if needed"""
    
    sql = """
    -- Course Categories Table
    CREATE TABLE IF NOT EXISTS course_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        color VARCHAR(7) DEFAULT '#7c3aed',
        icon VARCHAR(50) DEFAULT '📚',
        sort_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Courses Table  
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        youtube_video_id VARCHAR(20) NOT NULL,
        duration_minutes INTEGER DEFAULT 0,
        difficulty_level VARCHAR(20) DEFAULT 'beginner',
        thumbnail_url VARCHAR(500),
        cpe_credits REAL DEFAULT 0.0,
        is_required BOOLEAN DEFAULT 0,
        prerequisites TEXT,
        category_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES course_categories (id)
    );

    -- User Course Progress Table
    CREATE TABLE IF NOT EXISTS user_course_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        completed BOOLEAN DEFAULT 0,
        completed_at DATETIME,
        watch_time_minutes INTEGER DEFAULT 0,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (course_id) REFERENCES courses (id),
        UNIQUE(user_id, course_id)
    );

    -- User Education Stats Table (for performance)
    CREATE TABLE IF NOT EXISTS user_education_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        total_courses_completed INTEGER DEFAULT 0,
        total_learning_time_minutes INTEGER DEFAULT 0,
        total_cpe_credits_earned REAL DEFAULT 0.0,
        overall_progress_percentage REAL DEFAULT 0.0,
        last_course_completed_at DATETIME,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category_id);
    CREATE INDEX IF NOT EXISTS idx_courses_active ON courses(is_active);
    CREATE INDEX IF NOT EXISTS idx_progress_user ON user_course_progress(user_id);
    CREATE INDEX IF NOT EXISTS idx_progress_course ON user_course_progress(course_id);
    CREATE INDEX IF NOT EXISTS idx_progress_completed ON user_course_progress(completed);
    """
    
    return sql

def print_setup_instructions():
    """Print setup instructions for the development team"""
    instructions = """
    
PROFESSIONAL EDUCATION CENTER SETUP INSTRUCTIONS
==================================================

1. Add the models to your app:
   - Copy education.py to app/models/education.py
   - Add to app/models/__init__.py: from .education import *

2. Register the routes:
   - Copy education_routes.py to app/routers/education_routes.py
   - Add to your main app: app.register_blueprint(education_bp)

3. Run database setup:
   - Option A: python database/seed_education_data.py
   - Option B: Use Flask-Migrate: flask db migrate -m "Add education tables"

4. Update your navigation:
   - Add link to /education in your main navigation
   - Update the education.html template to use the new API endpoints

5. Frontend Integration:
   - Replace hardcoded progress with API calls to /api/education/progress/stats
   - Add "Mark Complete" buttons that call /api/education/progress/mark-complete
   - Update video grid to use /api/education/courses

BROKERAGE DEMO FEATURES:
- Real progress tracking with database persistence
- Professional course content for experienced agents
- CPE credit tracking for compliance
- Team analytics dashboard
- Advanced filtering and search
- Mobile-responsive design

This system will impress brokerages with its professional approach and comprehensive tracking!
"""
    print(instructions)

if __name__ == "__main__":
    print_setup_instructions()