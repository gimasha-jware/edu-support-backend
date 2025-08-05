from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Student(db.Model):
    __tablename__ = "students"

    sid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    qualification_level = db.Column(db.Enum('school', 'o/l', 'a/l', 'undergraduate', 'graduate'), default='school')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'sid': self.sid,
            'user_id': self.user_id,
            'age': self.age,
            'qualification_level': self.qualification_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
