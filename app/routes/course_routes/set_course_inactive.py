from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
from app.extensions import db
from app.utils.role_checker import roles_required
import logging

logger = logging.getLogger(__name__)

@jwt_required()
@roles_required('super_admin', 'admin')
def set_course_inactive(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        if not course.is_active:
            return jsonify({'message': 'Course is already inactive'}), 200

        course.is_active = False
        db.session.commit()

        logger.info(f"Course {course_id} marked as inactive")
        return jsonify({'message': f'Course {course_id} set to inactive successfully'}), 200

    except Exception as e:
        logger.error(f"Failed to set course inactive: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update course status', 'details': str(e)}), 500
