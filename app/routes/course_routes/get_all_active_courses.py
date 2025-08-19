from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
import logging

logger = logging.getLogger(__name__)

@jwt_required()
def get_all_active_courses():
    try:
        courses = Course.query.filter_by(is_active=True).order_by(Course.created_at.desc()).all()

        if not courses:
            return jsonify({'message': 'No active courses found'}), 200

        courses_list = [course.to_dict() for course in courses]
        logger.info(f"Fetched {len(courses_list)} active courses")
        return jsonify(courses_list), 200
    except Exception as e:
        logger.error(f"Failed to fetch active courses: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch courses', 'details': str(e)}), 500


