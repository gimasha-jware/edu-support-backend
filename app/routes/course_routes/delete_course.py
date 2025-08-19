import logging
from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
from app.models.course_stream import CourseStream
from app.models.course_location import CourseLocation
from app.models.course_education_mode import CourseEducationMode
from app.extensions import db
from app.utils.role_checker import roles_required

logger = logging.getLogger(__name__)

@jwt_required()
@roles_required('super_admin', 'admin')
def delete_course(course_id):

  try:
    course = Course.query.get(course_id)

    if not course:
      return jsonify({"error": "Course not found"}), 404
    
    # Delete all related records
    CourseStream.query.filter_by(course_id=course_id).delete()
    CourseLocation.query.filter_by(course_id=course_id).delete()
    CourseEducationMode.query.filter_by(course_id=course_id).delete()

    logger.info(f"Deleted related records")

    # Delete course
    db.session.delete(course)
    db.session.commit()

    logger.info(f"Deleted course")
    return jsonify({"message": "Course deleted successfully"}), 200

  except Exception as e:
    db.session.rollback()
    logger.error(f"Failed to delete course {course_id}: {e}", exc_info=True)
    return jsonify({'error': 'Course delete failed', 'details': str(e)}), 500


  
