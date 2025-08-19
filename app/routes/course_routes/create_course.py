import logging
from typing import List, Set
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

def validate_create_course_payload(data: dict) -> List[str]:
  required_fields = [
    'title', 'institute_type', 'category',
    'course_duration', 'course_fee',
    'install_availability', 'course_level'
  ]

  errors = []

  for field in required_fields:
    if field not in data:
      return jsonify({"error": f"{field} is required"}), 400
      errors.append(f"'{field}' is required")

  education_modes = data.get('education_modes')
  if not education_modes or not isinstance(education_modes, list) or len(education_modes) == 0:
    errors.append("At least one education mode is required")
  
  return errors

@jwt_required()
@roles_required('super_admin', 'admin')
def create_course():
  data = request.get_json()
  logger.info(f"Create course request data: {data}")

  if not data:
    return jsonify({"error": "No data provided"}), 400
  
  # Validate data
  errors = validate_create_course_payload(data)
  if errors:
    return jsonify({"errors": errors}), 400
  
  
  try:
    course = Course(
            title=data['title'],
            description=data.get('description'),
            sub_content=data.get('sub_content'),
            institute_type=data['institute_type'],
            category=data['category'],
            course_duration=data['course_duration'],
            course_fee=data['course_fee'],
            install_availability=data['install_availability'],
            instructor=data.get('instructor'),
            course_level=data['course_level']
        )

    # Normalize and add streams
    required_streams = normalize_strings(data.get('streams', []))
    for stream_name in required_streams:
      course.streams.append(CourseStream(stream=stream_name))

    # Normalize and add locations
    locations = normalize_strings(data.get('locations', []))
    for location_name in locations:
      course.locations.append(CourseLocation(location=location_name))

    # Normalize and add education modes
    education_modes = normalize_strings(data.get('education_modes', []))
    for edu_mode in education_modes:
      course.education_modes.append(CourseEducationMode(education_mode=edu_mode))

    db.session.add(course)
    db.session.commit()
    
    logger.info(f"Course created successfully with id: {course.id}")
    return jsonify(course.to_dict()), 201

  except Exception as e:
    db.session.rollback()
    logger.error(f"Course creation failed: {e}", exc_info=True)
    return jsonify({'error': 'Course creation failed', 'details': str(e)}), 500
  
