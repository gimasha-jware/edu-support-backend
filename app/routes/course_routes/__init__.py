from flask import Blueprint
from app.routes.course_routes.create_course import create_course

course_bp = Blueprint('course', __name__)

course_bp.route('/add', methods=['POST'])(create_course)

