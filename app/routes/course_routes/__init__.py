from flask import Blueprint
from app.routes.course_routes.create_course import create_course
from app.routes.course_routes.update_course import update_course
from app.routes.course_routes.delete_course import delete_course
from app.routes.course_routes.get_all_active_courses import get_all_active_courses
from app.routes.course_routes.set_course_inactive import set_course_inactive

course_bp = Blueprint('course', __name__)

course_bp.route('/add', methods=['POST'])(create_course)
course_bp.route('/update/<int:course_id>', methods=['PUT', 'PATCH'])(update_course)
course_bp.route('/delete/<int:course_id>', methods=['DELETE'])(delete_course)
course_bp.route('/active', methods=['GET'])(get_all_active_courses)
course_bp.route('/inactive/<int:course_id>', methods=['PUT', 'PATCH'])(set_course_inactive)


