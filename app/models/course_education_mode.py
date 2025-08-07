from app.extensions import db

class CourseEducationMode(db.Model):
    __tablename__ = "course_education_mode"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    education_mode = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'education_mode': self.education_mode
        }
