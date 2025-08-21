import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_extension(filename):
    return filename.rsplit(".", 1)[-1].lower()

def allowed_file(filename):
    ext = get_file_extension(filename)
    return ext in ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS)
