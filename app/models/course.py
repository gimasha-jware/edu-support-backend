from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sub_content = db.Column(db.String(140), nullable=True)
    institute_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    course_duration = db.Column(db.Integer, nullable=False)
    course_fee = db.Column(db.Numeric(10, 2), nullable=False)
    install_availability = db.Column(db.Boolean, nullable=False)
    instructor = db.Column(db.String(100), nullable=True)
    course_level = db.Column(db.Enum(
        'primary education', 'junior education', 'ordinary level', 'advanced level',
        'certificate', 'NVQ', 'diploma', 'higher national diploma', 'degree', 'masters', 'PhD'
    ), nullable=False)
    age_group = db.Column(db.String(50), nullable=True)
    minimum_z_score = db.Column(db.String(10), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    streams = relationship("CourseStream", backref="course")
    locations = relationship("CourseLocation", backref="course")
    education_modes = relationship("CourseEducationMode", backref="course")
    media_items = relationship("CourseMedia", backref="course") 

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'sub_content': self.sub_content,
            'institute_type': self.institute_type,
            'category': self.category,
            'course_duration': self.course_duration,
            'course_fee': float(self.course_fee),
            'install_availability': self.install_availability,
            'instructor': self.instructor,
            'course_level': self.course_level,
            'age_group': self.age_group,
            'minimum_z_score': self.minimum_z_score,
            'streams': [s.stream for s in self.streams],
            'locations': [l.location for l in self.locations],
            'education_modes': [e.education_mode for e in self.education_modes],
            'medias': [m.to_dict() for m in self.media_items],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
