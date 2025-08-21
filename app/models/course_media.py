from app.extensions import db

class CourseMedia(db.Model):
  __tablename__ = "course_media"

  id = db.Column(db.Integer, primary_key=True)
  course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
  media_type = db.Column(db.String(10), nullable=False)
  media_url = db.Column(db.String(255), nullable=True)

  def to_dict(self):
    return {
      'id': self.id,
      'course_id': self.course_id,
      'media_type': self.media_type,
      'media_url': self.media_url
    }