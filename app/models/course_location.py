from app.extensions import db

class CourseLocation(db.Model):
    __tablename__ = "course_locations"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'location': self.location
        }
