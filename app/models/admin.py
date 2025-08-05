from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Admin(db.Model):
    __tablename__ = "admins"

    aid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    role_description = db.Column(db.String(255), nullable=True) 
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'aid': self.aid,
            'user_id': self.user_id,
            'role_description': self.role_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
