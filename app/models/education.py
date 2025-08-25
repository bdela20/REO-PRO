# app/models/education.py

from app.models import db
from datetime import datetime
from sqlalchemy import func

class CourseCategory(db.Model):
    __tablename__ = 'course_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#7c3aed')  # Hex color for UI
    icon = db.Column(db.String(50), default='📚')  # Emoji or icon class
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', back_populates='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<CourseCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'course_count': self.courses.count()
        }

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    youtube_video_id = db.Column(db.String(20), nullable=False)  # YouTube video ID
    duration_minutes = db.Column(db.Integer, default=0)  # Video duration
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    thumbnail_url = db.Column(db.String(500))  # YouTube thumbnail
    
    # Professional features for brokerages
    cpe_credits = db.Column(db.Float, default=0.0)  # Continuing Education credits
    is_required = db.Column(db.Boolean, default=False)  # Required for certification
    prerequisites = db.Column(db.Text)  # JSON string of prerequisite course IDs
    
    # Category relationship
    category_id = db.Column(db.Integer, db.ForeignKey('course_categories.id'), nullable=False)
    category = db.relationship('CourseCategory', back_populates='courses')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Relationships
    user_progress = db.relationship('UserCourseProgress', back_populates='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.title}>'
    
    @property
    def completion_rate(self):
        """Calculate what percentage of users have completed this course"""
        total_users = self.user_progress.count()
        if total_users == 0:
            return 0
        completed_users = self.user_progress.filter_by(completed=True).count()
        return round((completed_users / total_users) * 100, 1)
    
    def to_dict(self, user_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'youtube_video_id': self.youtube_video_id,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'thumbnail_url': f'https://img.youtube.com/vi/{self.youtube_video_id}/maxresdefault.jpg',
            'cpe_credits': self.cpe_credits,
            'is_required': self.is_required,
            'category': self.category.to_dict(),
            'completion_rate': self.completion_rate,
            'created_at': self.created_at.isoformat()
        }
        
        # Add user-specific progress if user_id provided
        if user_id:
            progress = self.user_progress.filter_by(user_id=user_id).first()
            data['user_progress'] = {
                'completed': progress.completed if progress else False,
                'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None,
                'watch_time_minutes': progress.watch_time_minutes if progress else 0
            }
        
        return data

class UserCourseProgress(db.Model):
    __tablename__ = 'user_course_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Assumes you have users table
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Progress tracking
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    watch_time_minutes = db.Column(db.Integer, default=0)  # For analytics
    
    # Metadata
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='user_progress')
    # user = db.relationship('User', backref='course_progress')  # Uncomment when you have User model
    
    # Unique constraint - one progress record per user per course
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    def __repr__(self):
        return f'<UserCourseProgress user_id={self.user_id} course_id={self.course_id} completed={self.completed}>'
    
    def mark_completed(self):
        """Mark course as completed"""
        self.completed = True
        self.completed_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'course_id': self.course_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'watch_time_minutes': self.watch_time_minutes,
            'started_at': self.started_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }

class UserEducationStats(db.Model):
    """Summary statistics for user education progress - for performance"""
    __tablename__ = 'user_education_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Summary stats
    total_courses_completed = db.Column(db.Integer, default=0)
    total_learning_time_minutes = db.Column(db.Integer, default=0)
    total_cpe_credits_earned = db.Column(db.Float, default=0.0)
    
    # Progress tracking
    overall_progress_percentage = db.Column(db.Float, default=0.0)
    last_course_completed_at = db.Column(db.DateTime)
    
    # Metadata
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserEducationStats user_id={self.user_id}>'
    
    @classmethod
    def update_user_stats(cls, user_id):
        """Recalculate and update user statistics"""
        # Get user's progress
        progress_records = UserCourseProgress.query.filter_by(user_id=user_id).all()
        completed_courses = [p for p in progress_records if p.completed]
        
        # Calculate stats
        total_completed = len(completed_courses)
        total_learning_time = sum(p.watch_time_minutes for p in progress_records)
        total_cpe_credits = sum(p.course.cpe_credits for p in completed_courses)
        
        # Calculate overall progress (completed courses / total active courses)
        total_active_courses = Course.query.filter_by(is_active=True).count()
        progress_percentage = (total_completed / total_active_courses * 100) if total_active_courses > 0 else 0
        
        # Update or create stats record
        stats = cls.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = cls(user_id=user_id)
            db.session.add(stats)
        
        stats.total_courses_completed = total_completed
        stats.total_learning_time_minutes = total_learning_time
        stats.total_cpe_credits_earned = total_cpe_credits
        stats.overall_progress_percentage = round(progress_percentage, 1)
        
        if completed_courses:
            stats.last_course_completed_at = max(p.completed_at for p in completed_courses)
        
        db.session.commit()
        return stats
    
    def to_dict(self):
        return {
            'total_courses_completed': self.total_courses_completed,
            'total_learning_time_minutes': self.total_learning_time_minutes,
            'total_learning_time_hours': round(self.total_learning_time_minutes / 60, 1),
            'total_cpe_credits_earned': self.total_cpe_credits_earned,
            'overall_progress_percentage': self.overall_progress_percentage,
            'last_course_completed_at': self.last_course_completed_at.isoformat() if self.last_course_completed_at else None
        }