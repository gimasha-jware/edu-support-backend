from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserType
# from app.models.admin import Student, Institute
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def auth():
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
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        user_type = data.get('user_type')
        
        # Validate required fields
        required_fields = ['email', 'first_name', 'last_name', 'password', 'user_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email,
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Validate user_type using value (case-insensitive)
        try:
            user_type = get_usertype_from_value(user_type)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        
        # Create new user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_type=user_type
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
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
        print(f"User found: {user}, user_type: {user.user_type if user else 'None'}")

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
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

