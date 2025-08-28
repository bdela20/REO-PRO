# app/routers/education_routes.py

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user  # Adjust based on your auth system
from app.models.education import Course, CourseCategory, UserCourseProgress, UserEducationStats
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta
import logging
from app.models import db 

education_bp = Blueprint('education', __name__, url_prefix='/api/education')

# ============================================================================
# PUBLIC ROUTES (Course Catalog)
# ============================================================================

@education_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all course categories with course counts"""
    try:
        categories = CourseCategory.query.order_by(CourseCategory.sort_order, CourseCategory.name).all()
        
        return jsonify({
            'success': True,
            'categories': [cat.to_dict() for cat in categories]
        })
    
    except Exception as e:
        logging.error(f"Error fetching categories: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch categories'}), 500

@education_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get courses with optional filtering and user progress"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        difficulty = request.args.get('difficulty')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, title, difficulty, duration
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 12, type=int), 50)  # Max 50 per page
        
        # Build query
        query = Course.query.filter_by(is_active=True)
        
        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        
        if search:
            query = query.filter(
                db.or_(
                    Course.title.ilike(f'%{search}%'),
                    Course.description.ilike(f'%{search}%')
                )
            )
        
        # Apply sorting
        if sort_by == 'title':
            order_by = Course.title.asc() if sort_order == 'asc' else Course.title.desc()
        elif sort_by == 'duration':
            order_by = Course.duration_minutes.asc() if sort_order == 'asc' else Course.duration_minutes.desc()
        elif sort_by == 'difficulty':
            # Custom difficulty ordering: beginner < intermediate < advanced
            difficulty_order = db.case(
                (Course.difficulty_level == 'beginner', 1),
                (Course.difficulty_level == 'intermediate', 2),
                (Course.difficulty_level == 'advanced', 3),
                else_=0
            )
            order_by = difficulty_order.asc() if sort_order == 'asc' else difficulty_order.desc()
        else:  # created_at (default)
            order_by = Course.created_at.asc() if sort_order == 'asc' else Course.created_at.desc()
        
        query = query.order_by(order_by, Course.sort_order)
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get user ID for progress data (use dummy user for testing)
        user_id = 1  # Dummy user ID for testing
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            user_id = current_user.id
        
        # Convert to dict with user progress
        courses = [course.to_dict(user_id=user_id) for course in pagination.items]
        
        return jsonify({
            'success': True,
            'courses': courses,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'category_id': category_id,
                'difficulty': difficulty,
                'search': search
            }
        })
    
    except Exception as e:
        logging.error(f"Error fetching courses: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch courses'}), 500

@education_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course_detail(course_id):
    """Get detailed information about a specific course"""
    try:
        course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        # Get user ID for progress data (use dummy user for testing)
        user_id = 1  # Dummy user ID for testing
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            user_id = current_user.id
        
        return jsonify({
            'success': True,
            'course': course.to_dict(user_id=user_id)
        })
    
    except Exception as e:
        logging.error(f"Error fetching course {course_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch course'}), 500

# ============================================================================
# USER PROGRESS ROUTES (Temporarily no login required for testing)
# ============================================================================

@education_bp.route('/progress/stats', methods=['GET'])
# @login_required  # Commented out for testing
def get_user_stats():
    """Get user's overall education statistics"""
    try:
        # Use dummy user ID for testing
        user_id = 1
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            user_id = current_user.id
        
        # Update stats first (in production, this would be done via background job)
        stats = UserEducationStats.update_user_stats(user_id)
        
        # Get additional detailed stats
        recent_progress = UserCourseProgress.query.filter_by(
            user_id=user_id
        ).filter(
            UserCourseProgress.last_accessed >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Get category breakdown
        category_stats = db.session.query(
            CourseCategory.name,
            CourseCategory.color,
            func.count(UserCourseProgress.id).filter(UserCourseProgress.completed == True).label('completed'),
            func.count(Course.id).label('total')
        ).select_from(CourseCategory).join(
            Course, CourseCategory.id == Course.category_id
        ).outerjoin(
            UserCourseProgress,
            db.and_(
                UserCourseProgress.course_id == Course.id,
                UserCourseProgress.user_id == user_id
            )
        ).filter(Course.is_active == True).group_by(
            CourseCategory.id, CourseCategory.name, CourseCategory.color
        ).all()
        
        category_breakdown = [
            {
                'category': stat.name,
                'color': stat.color,
                'completed': stat.completed,
                'total': stat.total,
                'percentage': round((stat.completed / stat.total * 100) if stat.total > 0 else 0, 1)
            }
            for stat in category_stats
        ]
        
        return jsonify({
            'success': True,
            'stats': {
                **stats.to_dict(),
                'recent_activity_courses': recent_progress,
                'category_breakdown': category_breakdown
            }
        })
    
    except Exception as e:
        logging.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500

@education_bp.route('/progress/mark-complete', methods=['POST'])
def mark_course_complete():
    """Mark a course as completed for the current user"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        watch_time = data.get('watch_time_minutes', 0)
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Course ID is required'}), 400
        
        # Verify course exists
        course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        user_id = 1
        
        # Get or create progress record
        progress = UserCourseProgress.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not progress:
            progress = UserCourseProgress(
                user_id=user_id,
                course_id=course_id,
                watch_time_minutes=0
            )
            db.session.add(progress)
        
        # Update progress
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        progress.last_accessed = datetime.utcnow()
        current_watch_time = progress.watch_time_minutes or 0
        progress.watch_time_minutes = max(current_watch_time, watch_time)
        
        # Calculate and update user statistics
        total_completed = UserCourseProgress.query.filter_by(user_id=user_id, completed=True).count()
        total_active_courses = Course.query.filter_by(is_active=True).count()
        progress_percentage = (total_completed / total_active_courses * 100) if total_active_courses > 0 else 0
        
        # Update or create stats record
        stats = UserEducationStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserEducationStats(user_id=user_id)
            db.session.add(stats)
        
        stats.total_courses_completed = total_completed
        stats.overall_progress_percentage = round(progress_percentage, 1)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course marked as completed!',
            'cpe_credits_earned': course.cpe_credits,
            'new_stats': {
                'total_completed': total_completed,
                'progress_percentage': round(progress_percentage, 1)
            }
        })
    
    except Exception as e:
        logging.error(f"Error marking course complete: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@education_bp.route('/progress/update-watch-time', methods=['POST'])
# @login_required  # Commented out for testing
def update_watch_time():
    """Update watch time for a course (for analytics)"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        watch_time = data.get('watch_time_minutes', 0)
        
        if not course_id or watch_time < 0:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
        
        # Use dummy user ID for testing
        user_id = 1
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            user_id = current_user.id
        
        # Get or create progress record
        progress = UserCourseProgress.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not progress:
            progress = UserCourseProgress(
                user_id=user_id,
                course_id=course_id
            )
            db.session.add(progress)
        
        # Update watch time and last accessed
        progress.watch_time_minutes = max(progress.watch_time_minutes, watch_time)
        progress.last_accessed = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'watch_time_updated': progress.watch_time_minutes
        })
    
    except Exception as e:
        logging.error(f"Error updating watch time: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to update watch time'}), 500

@education_bp.route('/progress/my-courses', methods=['GET'])
# @login_required  # Commented out for testing
def get_my_courses():
    """Get user's course progress with filtering options"""
    try:
        status = request.args.get('status')  # 'completed', 'in_progress', 'not_started'
        
        # Use dummy user ID for testing
        user_id = 1
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            user_id = current_user.id
        
        # Base query - all active courses with user progress
        query = db.session.query(Course, UserCourseProgress).outerjoin(
            UserCourseProgress,
            db.and_(
                UserCourseProgress.course_id == Course.id,
                UserCourseProgress.user_id == user_id
            )
        ).filter(Course.is_active == True)
        
        # Apply status filter
        if status == 'completed':
            query = query.filter(UserCourseProgress.completed == True)
        elif status == 'in_progress':
            query = query.filter(
                db.and_(
                    UserCourseProgress.id.isnot(None),
                    UserCourseProgress.completed == False
                )
            )
        elif status == 'not_started':
            query = query.filter(UserCourseProgress.id.is_(None))
        
        results = query.order_by(Course.created_at.desc()).all()
        
        courses = []
        for course, progress in results:
            course_data = course.to_dict(user_id=user_id)
            courses.append(course_data)
        
        return jsonify({
            'success': True,
            'courses': courses,
            'total': len(courses)
        })
    
    except Exception as e:
        logging.error(f"Error fetching user courses: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch courses'}), 500

# ============================================================================
# ANALYTICS ROUTES (For Brokerage Dashboards)
# ============================================================================

@education_bp.route('/analytics/overview', methods=['GET'])
# @login_required  # Commented out for testing
def get_analytics_overview():
    """Get system-wide education analytics (for admin/brokerage dashboards)"""
    try:
        # This would typically require admin permissions
        # For demo purposes, showing aggregate stats
        
        # Total system stats
        total_courses = Course.query.filter_by(is_active=True).count()
        total_categories = CourseCategory.query.count()
        
        # User engagement stats
        active_users = db.session.query(UserCourseProgress.user_id).distinct().count()
        total_completions = UserCourseProgress.query.filter_by(completed=True).count()
        
        # Most popular courses
        popular_courses = db.session.query(
            Course.title,
            func.count(UserCourseProgress.id).label('enrollments'),
            func.count(UserCourseProgress.id).filter(UserCourseProgress.completed == True).label('completions')
        ).join(UserCourseProgress).group_by(Course.id, Course.title).order_by(
            desc('enrollments')
        ).limit(5).all()
        
        # Recent activity
        recent_completions = db.session.query(
            Course.title,
            UserCourseProgress.completed_at
        ).join(Course).filter(
            UserCourseProgress.completed == True,
            UserCourseProgress.completed_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(desc(UserCourseProgress.completed_at)).limit(10).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'system_stats': {
                    'total_courses': total_courses,
                    'total_categories': total_categories,
                    'active_users': active_users,
                    'total_completions': total_completions,
                    'avg_completions_per_user': round(total_completions / active_users, 1) if active_users > 0 else 0
                },
                'popular_courses': [
                    {
                        'title': course.title,
                        'enrollments': course.enrollments,
                        'completions': course.completions,
                        'completion_rate': round((course.completions / course.enrollments * 100) if course.enrollments > 0 else 0, 1)
                    }
                    for course in popular_courses
                ],
                'recent_activity': [
                    {
                        'course_title': completion.title,
                        'completed_at': completion.completed_at.isoformat()
                    }
                    for completion in recent_completions
                ]
            }
        })
    
    except Exception as e:
        logging.error(f"Error fetching analytics: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch analytics'}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@education_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@education_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@education_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({'success': True, 'message': 'Education routes are working!'})