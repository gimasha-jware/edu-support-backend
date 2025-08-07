from flask import Flask, jsonify
from app.extensions import db, jwt, bcrypt
from flask_cors import CORS
from app.utils.config import config
import os
from app.routes.auth import auth_bp
from app.routes.course_routes import course_bp
from app.models import User, Student  # Import models to ensure they are registered

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(course_bp, url_prefix='/api/courses')
 
    return app

