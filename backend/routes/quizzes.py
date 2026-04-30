from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.quiz import Quiz
from models.user import User
from datetime import datetime

quizzes_bp = Blueprint('quizzes', __name__)
quiz_model = Quiz()
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

@quizzes_bp.route('/quizzes', methods=['POST'])
def create_quiz():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id):
            return jsonify({'error': 'Only teachers can create quizzes'}), 403

        data = request.json
        quiz_id = quiz_model.create_quiz(data)
        return jsonify({'message': 'Quiz created!', 'quiz_id': quiz_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/quizzes/<quiz_id>/attempt', methods=['POST'])
def attempt_quiz(quiz_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_student(current_user_id):
            return jsonify({'error': 'Only students can attempt quizzes'}), 403

        # Check if student is blocked
        user = user_model.find_by_id(current_user_id)
        if user.get('is_blocked', False):
            return jsonify({'error': 'Your account has been blocked'}), 403

        # Get quiz and check deadline
        from bson import ObjectId
        quiz = quiz_model.collection.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        due_date = quiz.get('due_date')
        if due_date:
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            if datetime.utcnow() > due_date:
                return jsonify({'error': 'Quiz deadline has passed'}), 400

        # Check if already attempted
        existing = next((a for a in quiz.get('attempts', []) if a['student_id'] == current_user_id), None)
        if existing:
            return jsonify({'error': 'You have already attempted this quiz'}), 400

        data = request.json
        success = quiz_model.attempt_quiz(quiz_id, current_user_id, data.get('answers', []))

        if success:
            return jsonify({'message': 'Quiz submitted successfully!'}), 200
        return jsonify({'error': 'Failed to submit quiz'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/quizzes/<quiz_id>/grade', methods=['POST'])
def grade_quiz(quiz_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Only teachers can grade quizzes'}), 403

        data = request.json
        student_id = data.get('student_id')
        marks = data.get('marks')

        if not student_id or marks is None:
            return jsonify({'error': 'student_id and marks are required'}), 400

        success = quiz_model.grade_quiz(quiz_id, student_id, marks)
        if success:
            return jsonify({'message': 'Quiz graded successfully!'}), 200
        return jsonify({'error': 'Failed to grade quiz'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/quizzes/<quiz_id>/attempts', methods=['GET'])
def get_quiz_attempts(quiz_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        from bson import ObjectId
        quiz = quiz_model.collection.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        quiz['_id'] = str(quiz['_id'])
        attempts = quiz.get('attempts', [])

        for attempt in attempts:
            student = user_model.find_by_id(attempt['student_id'])
            if student:
                attempt['student_name'] = student['name']
                attempt['student_email'] = student['email']

        return jsonify({'quiz': quiz, 'attempts': attempts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        from bson import ObjectId
        result = quiz_model.collection.delete_one({'_id': ObjectId(quiz_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Quiz deleted!'}), 200
        return jsonify({'error': 'Quiz not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
