from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models.attendance import Attendance
from backend.models.user import User

attendance_bp = Blueprint('attendance', __name__)
attendance_model = Attendance()
user_model = User()

def is_teacher(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'teacher'

@attendance_bp.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if not is_teacher(current_user_id):
            return jsonify({'error': 'Only teachers can mark attendance'}), 403
        
        data = request.json
        success = attendance_model.mark_attendance(data['course_id'], data['student_id'], data['status'])
        
        if success:
            return jsonify({'message': 'Attendance marked!'}), 200
        return jsonify({'error': 'Failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance/my-attendance', methods=['GET'])
def get_my_attendance():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        course_id = request.args.get('course_id')
        attendance = attendance_model.get_student_attendance(current_user_id, course_id)
        
        for a in attendance:
            a['_id'] = str(a['_id'])
        return jsonify(attendance), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500