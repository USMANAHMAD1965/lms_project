from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import sys

load_dotenv()

from backend.routes.auth import auth_bp
from backend.routes.courses import courses_bp
from backend.routes.assignments import assignments_bp
from backend.routes.quizzes import quizzes_bp
from backend.routes.attendance import attendance_bp
from backend.utils.db import MongoDB
from backend.middleware.auth_middleware import check_blocked_user

app = Flask(__name__, static_folder='../frontend', static_url_path='')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
CORS(app)
jwt = JWTManager(app)

# Connect to MongoDB
try:
    MongoDB.connect()
    print("[OK] MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    sys.exit(1)

# Blocked user check on every API request
app.before_request(check_blocked_user)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(courses_bp, url_prefix='/api')
app.register_blueprint(assignments_bp, url_prefix='/api')
app.register_blueprint(quizzes_bp, url_prefix='/api')
app.register_blueprint(attendance_bp, url_prefix='/api')

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/pages/<path:path>')
def pages(path):
    return send_from_directory('../frontend/pages', path)

@app.route('/css/<path:path>')
def css(path):
    return send_from_directory('../frontend/css', path)

@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('../frontend/js', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)