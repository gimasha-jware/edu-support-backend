from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course
from app.models.course_stream import CourseStream
from app.models.course_location import CourseLocation
from app.models.course_education_mode import CourseEducationMode
from app.extensions import db
from app.utils.role_checker import roles_required

@jwt_required()
@roles_required('super_admin', 'admin')
def create_course():
  data = request.get_json()

  required_fields = [
    'title', 'institute_type', 'category',
    'course_duration', 'course_fee',
    'install_availability', 'course_level'
  ]

  for field in required_fields:
    if field not in data:
      return jsonify({"error": f"{field} is required"}), 400
    
  if 'locations' not in data or not isinstance(data['locations'], list) or len(data['locations']) == 0:
    return jsonify({'error': "At least one location is required"}), 400

  if 'education_modes' not in data or not isinstance(data['education_modes'], list) or len(data['education_modes']) == 0:
    return jsonify({'error': "At least one education mode is required"}), 400
  
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

    required_streams = data.get('streams', [])
    for stream_name in required_streams:
      course.streams.append(CourseStream(stream=stream_name))

    locations = data.get('locations', [])
    for location_name in locations:
      course.locations.append(CourseLocation(location=location_name))

    education_modes = data.get('education_modes', [])
    for edu_mode in education_modes:
      course.education_modes.append(CourseEducationMode(education_mode=edu_mode))

    db.session.add(course)
    db.session.commit()
    # print("Course created")
    return jsonify(course.to_dict()), 201

  except Exception as e:
        db.session.rollback()
        print("error", str(e))
        return jsonify({'error': 'Course creation failed', 'details': str(e)}), 500
  
