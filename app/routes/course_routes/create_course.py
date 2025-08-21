import os
import logging
import json
from typing import List, Set, Dict
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
from app.models.course_stream import CourseStream
from app.models.course_location import CourseLocation
from app.models.course_education_mode import CourseEducationMode
from app.models.course_media import CourseMedia
from app.extensions import db
from app.utils.role_checker import roles_required
from app.utils.file_utils import UPLOAD_FOLDER, allowed_file, get_file_extension, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS
from app.routes.course_routes.utils.normalize_course_data import normalize_course_data

from werkzeug.utils import secure_filename

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
    if field not in data or data[field] is None or str(data[field]).strip() == "":
      errors.append(f"'{field}' is required")

  education_modes = data.get('education_modes')
  if not education_modes or not isinstance(education_modes, list) or len(education_modes) == 0:
    errors.append("At least one education mode is required")

  # Normalized install_availability, course_duration and course_fee
  normlized_data , error = normalize_course_data(data)
  if error:
    logger.error("Invalid input of install_avalibility")
    errors.append(error)
  else:
    data = normlized_data
    logger.info("Assigned normalized data into data")

  return errors

# Media validations
def validate_media(media_items: List[Dict]) -> List[str]:

  media_errors = []
  allowed_photo_limit = 3
  allowed_video_limit = 1
  
  # Count media types
  photos = [m for m in media_items if m.get("media_type") in ALLOWED_IMAGE_EXTENSIONS]
  videos = [m for m in media_items if m.get("media_type") in ALLOWED_VIDEO_EXTENSIONS]

  if len(photos) > allowed_photo_limit:
    media_errors.append(f"Maximum 3 photos allowed")
  if len(videos) > allowed_video_limit:
    media_errors.append(f"Maximum 1 video allowed")

  return media_errors

def save_media_files(files: List) -> List[Dict]:
  saved_items = []

  for file in files:
    if not allowed_file(file.filename):
      continue

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    saved_items.append({
      "media_type": get_file_extension(filename),
      "media_url": file_path
    })

  return saved_items;

@jwt_required()
@roles_required('super_admin', 'admin')
def create_course():
  data = request.form.to_dict()

  # Convert JSON string fields to lists
  for field in ["streams", "locations", "education_modes"]:
      if field in data:
          try:
              data[field] = json.loads(data[field])
              if not isinstance(data[field], list):
                  return jsonify({"error": f"'{field}' must be a list"}), 400
          except json.JSONDecodeError:
              return jsonify({"error": f"Invalid JSON for field '{field}'"}), 400

  # Validate data
  errors = validate_create_course_payload(data)
  if errors:
    return jsonify({"errors": errors}), 400
  
  logger.info(f"Create course request data: {data}")

  # Save media files
  media_files = request.files.getlist("media_files")
  media_items = save_media_files(media_files) if media_files else []
  
  # Validate course media
  media_errors = validate_media(media_items)
  if media_errors:
    return jsonify({"errors": media_errors}), 400
  
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
            course_level=data['course_level'],
            age_group=data['age_group'],
            minimum_z_score=data['minimum_z_score'],
        )
    
    # Add media items
    for item in media_items:
      course.media_items.append(CourseMedia(
        media_type=item["media_type"],
        media_url=item["media_url"]
      ))

    # Normalize and add streams, locations, education_modes
    required_streams = normalize_strings(data.get('streams', []))
    for stream_name in required_streams:
      course.streams.append(CourseStream(stream=stream_name))

    locations = normalize_strings(data.get('locations', []))
    for location_name in locations:
      course.locations.append(CourseLocation(location=location_name))

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
  
