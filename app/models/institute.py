from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Institute(db.Model):
    __tablename__ = 'institutes'

    iid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), unique=True, nullable=False)
    legal_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    billing_address = db.Column(db.Text, nullable=False)
    vat_number = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "iid": self.iid,
            "user_id": self.user_id,
            "legal_name": self.legal_name,
            "address": self.address,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "billing_address": self.billing_address,
            "vat_number": self.vat_number,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }



