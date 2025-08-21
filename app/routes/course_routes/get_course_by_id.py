import logging
from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course

logger = logging.getLogger(__name__)

@jwt_required()
def get_course_by_id(course_id):
    try:
        course = Course.query.get(course_id)

        if not course:
            logger.info(f"No course found with ID: {course_id}")
            return jsonify({"message": "Course not found"}), 404

        return jsonify(course.to_dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving course {course_id}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500