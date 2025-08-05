import enum
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import relationship

class UserType(Enum):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    STUDENT = 'student'
    INSTITUTE = 'institute'

    @staticmethod
    def from_str(label: str):
        label = label.lower()
        for user_type in UserType:
            if user_type.value == label:
                return user_type
        raise ValueError(f"Invalid user_type: {label}")

class User(db.Model):
    __tablename__ = 'users'
    
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum(UserType, native_enum=False, values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # One-to-one relationships
    student_profile = relationship("Student", backref="user", uselist=False)
    admin_profile = relationship("Admin", backref="user", uselist=False)
   
    def __init__(self, email, first_name, last_name, password, user_type):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)
        
        if isinstance(user_type, str):
            self.user_type = UserType.from_str(user_type)
        elif isinstance(user_type, UserType):
            self.user_type = user_type
        else:
            raise ValueError("Invalid user_type")
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        base ={
            'id': self.uid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_type': self.user_type.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
        # Attach profile data if available
        if self.user_type == UserType.STUDENT and self.student_profile:
            base["student_profile"] = self.student_profile.to_dict()
        elif self.user_type == UserType.INSTITUTE and self.institute_profile:
            base["institute_profile"] = self.institute_profile.to_dict()
        elif self.user_type == UserType.ADMIN and self.admin_profile:
            base["admin_profile"] = self.admin_profile.to_dict()

        return base
    
    def is_admin(self):
        """Check if user is admin or super admin"""
        return self.user_type in [UserType.ADMIN, UserType.SUPER_ADMIN]
    
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.user_type == UserType.SUPER_ADMIN
    
    def is_student(self):
        """Check if user is a student"""
        return self.user_type == UserType.STUDENT
    
    def __repr__(self):
        return f'<User {self.email} - {self.user_type.value}>'