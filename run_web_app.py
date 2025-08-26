from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST!

# ADD THIS NEW CODE BLOCK:
import os
if os.environ.get('RUN_SETUP'):
    print("🔧 Setting up database...")
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.models import db
        from app.models.education import CourseCategory, Course
        db.create_all()
        print("✅ Tables created")
        if CourseCategory.query.count() == 0:
            cat = CourseCategory(name="Commercial Real Estate", description="Advanced commercial property strategies", color="#7c3aed", icon="🏢")
            db.session.add(cat)
            db.session.commit()
            course = Course(title="Commercial Leasing Strategies", description="Master commercial lease negotiations", youtube_video_id="dQw4w9WgXcQ", duration_minutes=45, difficulty_level="advanced", cpe_credits=2.0, category_id=cat.id, is_active=True)
            db.session.add(course)
            db.session.commit()
            print("✅ Database setup complete!")

# YOUR EXISTING CODE:
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Real Estate Office Pro is running!")
    
    # Get port from environment (for production) or use 5001 for local
    port = int(os.environ.get('PORT', 5001))
    
    # Disable debug in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)