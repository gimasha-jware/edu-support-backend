from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserType
from app.models.student import Student
from app.models.institute import Institute
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def auth():
    logger.info("Auth route accessed")
    return jsonify({"message": "Auth route works!"})

# Case-insensitive UserType lookup
def get_usertype_from_value(value):
    try:
        return next(utype for utype in UserType if utype.value == value.lower())
    except StopIteration:
        raise ValueError(f"'{value}' is not a valid user type. Allowed: {[u.value for u in UserType]}")


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        logging.debug(f"[DEBUG] Registration data: {data}")
        
        # Validate required fields
        required_fields = ['email', 'first_name', 'last_name', 'password', 'user_type']
        logging.debug(f"[DEBUG] Registration data: {data}")
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        email = data['email']
        existing_user = User.query.filter_by(
            email=email,
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Validate user_type using value (case-insensitive)
        user_type = data['user_type']
        logging.debug(f"[DEBUG] User type from request: {user_type}")
        try:
            user_type = get_usertype_from_value(user_type)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        
        if user_type not in ['student', 'admin', 'super_admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        logging.debug(f"[DEBUG] User type validated: {user_type}")
        # Create new user
        new_user = User(
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
            user_type=user_type
        )
        logging.debug(f"[DEBUG] New user created: {new_user.email}, type: {new_user.user_type.value}")

        db.session.add(new_user)
        db.session.flush()  # Flush to get the user ID before creating profiles

        # Create user profile based on user type
        if user_type == UserType.STUDENT:
            student_profile = Student(
                user_id=new_user.uid,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(student_profile)
            logging.debug(f"[DEBUG] Student profile created for user: {new_user.email}")


        db.session.commit()
        logging.debug(f"[DEBUG] New user registered: {new_user.email}")

        return jsonify({"message": "User registered successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print("[ERROR] Exception occurred during registration:")
        traceback.print_exc()  # ✅ shows full error trace in terminal
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print(f"Login attempt with email: {email}") 

        if not data or not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()
        print(f"User found: {user}, user_type: {user.user_type.value if user else 'None'}")

        if user and user.user_type.value not in ['student', 'admin', 'super_admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create tokens
        access_token = create_access_token(identity={"id": user.uid, "user_type": user.user_type.value}, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity={"id":user.uid, "user_type": user.user_type.value}, expires_delta=timedelta(days=30))
        
        # Get additional user info based on user type
        user_info = user.to_dict()
        
        # if user.is_student() and user.student_profile:
        #     user_info['student_profile'] = user.student_profile.to_dict()
        # elif user.is_institute() and user.institute_profile:
        #     user_info['institute_profile'] = user.institute_profile.to_dict()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_info,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

