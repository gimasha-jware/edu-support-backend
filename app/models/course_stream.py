from app.extensions import db

class CourseStream(db.Model):
    __tablename__ = "course_streams"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    stream = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'stream': self.stream
        }
