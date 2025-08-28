# education_data.py - Single file to add all education content

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import db
from app.models.education import CourseCategory, Course

def add_education_content():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Force clear all existing courses
        print("Clearing existing courses...")
        for course in Course.query.all():
            db.session.delete(course)
        db.session.commit()
        print("Courses cleared")
        
        # Categories
        categories = [
            {'name': 'Commercial Real Estate', 'color': '#059669', 'description': 'Commercial property strategies'},
            {'name': 'Advanced Negotiation', 'color': '#2563eb', 'description': 'Master-level negotiation'},
        ]
        
        # Add categories
        cat_ids = {}
        for cat in categories:
            existing = CourseCategory.query.filter_by(name=cat['name']).first()
            if not existing:
                new_cat = CourseCategory(**cat)
                db.session.add(new_cat)
                db.session.flush()
                cat_ids[cat['name']] = new_cat.id
            else:
                cat_ids[cat['name']] = existing.id
        
        # Working test videos
        courses = [
            {'title': 'Test Course 1', 'description': 'Test description', 'youtube_video_id': 'dQw4w9WgXcQ', 'duration_minutes': 3, 'difficulty_level': 'beginner', 'category': 'Commercial Real Estate', 'cpe_credits': 0.5},
            {'title': 'Test Course 2', 'description': 'Test description', 'youtube_video_id': 'kJQP7kiw5Fk', 'duration_minutes': 4, 'difficulty_level': 'beginner', 'category': 'Advanced Negotiation', 'cpe_credits': 0.5},
        ]
        
        # Add courses
        print("Adding new courses...")
        for course in courses:
            new_course = Course(
                title=course['title'],
                description=course['description'],
                youtube_video_id=course['youtube_video_id'],
                duration_minutes=course['duration_minutes'],
                difficulty_level=course['difficulty_level'],
                cpe_credits=course['cpe_credits'],
                category_id=cat_ids[course['category']],
                is_active=True
            )
            db.session.add(new_course)
            print(f"Added: {course['title']}")
        
        db.session.commit()
        print("Done! Check your education page now.")

if __name__ == "__main__":
    add_education_content()
