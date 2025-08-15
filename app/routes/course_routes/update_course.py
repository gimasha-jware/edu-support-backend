import logging
from typing import List, Set,  Optional
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
from app.models.course_stream import CourseStream
from app.models.course_location import CourseLocation
from app.models.course_education_mode import CourseEducationMode
from app.extensions import db
from app.utils.role_checker import roles_required

logger = logging.getLogger(__name__)

def normalize_strings(items: List[str]) -> Set[str]:
  return {item.strip().lower() for item in items if isinstance(item, str)}
    
def validate_education_modes(modes: Optional[List[str]]) -> Optional[str]:
    """Validate education modes list."""
    if not modes or not isinstance(modes, list) or len(modes) == 0:
        return "At least one education mode is required"
    return None

def sync_course_items(model, course_id, field_name, new_values: List[str]):
    """
    Sync related course items (streams, locations, education modes)
    without deleting unchanged rows.
    """

    # Normalize incoming values
    normalized_new_values = normalize_strings(new_values)

    # Get current values fro DB
    current_values = {
        getattr(item, field_name).strip().lower()
        for item in model.query.filter_by(course_id=course_id).all()
    }
    
    # Find items to delete and insert
    delete_values = current_values - normalized_new_values
    new_values = normalized_new_values - current_values

    # Delete removed items
    if delete_values:
        model.query.filter(
            model.course_id == course_id,
            getattr(model, field_name).in_(delete_values)
        ).delete(synchronize_session=False)

    # Insert new items
    for value in new_values:
        db.session.add(model(course_id=course_id, **{field_name: value}))

@jwt_required()
@roles_required('super_admin', 'admin')
def update_course(course_id):
    data = request.get_json()
    logger.info(f"Update course request data: {data}")

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Find existing course
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Update major content if present
        major_fields = [
            'title', 'description', 'sub_content',
            'institute_type', 'category',
            'course_duration', 'course_fee',
            'install_availability', 'instructor',
            'course_level'
        ]
        for field in major_fields:
            if field in data:
                setattr(course, field, data[field])

        # Replace streams if provide
        if 'streams' in data:
            sync_course_items(CourseStream, course_id, 'stream', data['streams'])

        # Replace locations if provide
        if 'locations' in data:
            sync_course_items(CourseLocation, course_id, 'location', data['locations'])


        # Replace education modes if provide
        if 'education_modes' in data:
            error = validate_education_modes(data['education_modes'])
            if error:
                return jsonify({'error': error}), 400

            sync_course_items(CourseEducationMode, course_id, 'education_mode', data['education_modes'])

        db.session.commit()

        logger.info(f"Course {course_id} updated successfully.")

        return jsonify(course.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update course {course_id}: {e}", exc_info=True)
        return jsonify({'error': 'Course update failed', 'details': str(e)}), 500
