from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.db_utills import get_db_connection  

student_bp = Blueprint("student", __name__)

@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_student_profile():
    # `get_jwt_identity()`should set during login (here it's uid)
    identity = get_jwt_identity()
    print("JWT Identity:", identity)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch student details
    query = """
        SELECT 
            u.email,
            u.first_name,
            u.last_name,
            s.age,
            s.qualification_level
        FROM users u
        INNER JOIN students s ON u.uid = s.user_id
        WHERE u.uid = %s AND u.user_type = 'student'
    """
    cursor.execute(query, (identity,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student), 200
