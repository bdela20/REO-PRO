# quick_fix_production.py - FIXED VERSION

# Load environment exactly like run_web_app.py does
from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app

# Create app exactly like run_web_app.py does
app = create_app()

from app.models import db
from app.models.education import CourseCategory, Course
import sys

def create_tables_and_seed():
    """Create education tables and add seed data"""
    try:
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully")
        
        # Check if categories already exist
        if CourseCategory.query.count() > 0:
            print("Data already exists, skipping seed")
            return
        
        print("Adding seed data...")
        
        # Create categories
        categories = [
            {"name": "Commercial Real Estate", "description": "Advanced commercial property strategies", "color": "#7c3aed", "icon": "🏢"},
            {"name": "Advanced Negotiation", "description": "Master-level negotiation techniques", "color": "#059669", "icon": "🤝"},
        ]
        
        for i, cat_data in enumerate(categories):
            category = CourseCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                sort_order=i
            )
            db.session.add(category)
        
        db.session.commit()
        print("Categories created")
        
        # Create courses
        courses = [
            {
                "title": "Commercial Leasing Strategies for Agents",
                "description": "Master commercial lease negotiations, tenant improvements, and commercial property management.",
                "youtube_video_id": "dQw4w9WgXcQ",
                "duration_minutes": 45,
                "difficulty_level": "advanced",
                "cpe_credits": 2.0,
                "category_name": "Commercial Real Estate"
            },
            {
                "title": "Advanced Negotiation Psychology",
                "description": "Psychological principles and advanced tactics for complex real estate negotiations.",
                "youtube_video_id": "dQw4w9WgXcQ",
                "duration_minutes": 32,
                "difficulty_level": "intermediate",
                "cpe_credits": 1.0,
                "category_name": "Advanced Negotiation"
            }
        ]
        
        for course_data in courses:
            category = CourseCategory.query.filter_by(name=course_data["category_name"]).first()
            if category:
                course = Course(
                    title=course_data["title"],
                    description=course_data["description"],
                    youtube_video_id=course_data["youtube_video_id"],
                    duration_minutes=course_data["duration_minutes"],
                    difficulty_level=course_data["difficulty_level"],
                    cpe_credits=course_data["cpe_credits"],
                    category_id=category.id,
                    is_active=True
                )
                db.session.add(course)
        
        db.session.commit()
        print("Courses created successfully")
        print("Education system is now ready!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    # Run within Flask app context
    with app.app_context():
        create_tables_and_seed()