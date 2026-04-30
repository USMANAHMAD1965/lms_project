from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models.assignment import Assignment
from backend.models.user import User
from datetime import datetime

assignments_bp = Blueprint('assignments', __name__)
assignment_model = Assignment()
user_model = User()

def is_teacher(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'teacher'

def is_student(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'student'

def is_admin(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'admin'

@assignments_bp.route('/assignments', methods=['POST'])
def create_assignment():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id):
            return jsonify({'error': 'Only teachers can create assignments'}), 403

        data = request.json
        assignment_id = assignment_model.create_assignment(data)
        return jsonify({'message': 'Assignment created!', 'assignment_id': assignment_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<assignment_id>/submit', methods=['POST'])
def submit_assignment(assignment_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_student(current_user_id):
            return jsonify({'error': 'Only students can submit'}), 403

        # Check if student is blocked
        user = user_model.find_by_id(current_user_id)
        if user.get('is_blocked', False):
            return jsonify({'error': 'Your account has been blocked'}), 403

        # Check deadline
        from bson import ObjectId
        assignment = assignment_model.collection.find_one({'_id': ObjectId(assignment_id)})
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404

        due_date = assignment.get('due_date')
        if due_date:
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            if datetime.utcnow() > due_date:
                return jsonify({'error': 'Deadline has passed. Cannot submit after due date.'}), 400

        # Check if already submitted
        existing = next((s for s in assignment.get('submissions', []) if s['student_id'] == current_user_id), None)
        if existing:
            return jsonify({'error': 'You have already submitted this assignment'}), 400

        data = request.json
        success = assignment_model.submit_assignment(assignment_id, current_user_id, data)

        if success:
            return jsonify({'message': 'Assignment submitted successfully!'}), 200
        return jsonify({'error': 'Failed to submit assignment'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<assignment_id>/grade', methods=['POST'])
def grade_assignment(assignment_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Only teachers can grade assignments'}), 403

        data = request.json
        student_id = data.get('student_id')
        marks = data.get('marks')
        feedback = data.get('feedback', '')

        if not student_id or marks is None:
            return jsonify({'error': 'student_id and marks are required'}), 400

        success = assignment_model.grade_assignment(assignment_id, student_id, marks, feedback)
        if success:
            return jsonify({'message': 'Assignment graded successfully!'}), 200
        return jsonify({'error': 'Failed to grade assignment'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<assignment_id>/submissions', methods=['GET'])
def get_submissions(assignment_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        from bson import ObjectId
        assignment = assignment_model.collection.find_one({'_id': ObjectId(assignment_id)})
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404

        assignment['_id'] = str(assignment['_id'])
        submissions = assignment.get('submissions', [])

        # Enrich with student names
        for sub in submissions:
            student = user_model.find_by_id(sub['student_id'])
            if student:
                sub['student_name'] = student['name']
                sub['student_email'] = student['email']

        return jsonify({'assignment': assignment, 'submissions': submissions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        from bson import ObjectId
        result = assignment_model.collection.delete_one({'_id': ObjectId(assignment_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Assignment deleted!'}), 200
        return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
