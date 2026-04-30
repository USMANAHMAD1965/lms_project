from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models.course import Course
from backend.models.user import User

courses_bp = Blueprint('courses', __name__)
course_model = Course()
user_model = User()

# Helper functions
def is_admin(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'admin'

def is_teacher(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'teacher'

def is_student(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'student'

@courses_bp.route('/courses', methods=['POST'])
def create_new_course():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can create courses'}), 403

        data = request.json
        print(f"Creating course: {data.get('title')}")

        teacher = user_model.find_by_id(data['teacher_id'])
        if not teacher or teacher['role'] != 'teacher':
            return jsonify({'error': 'Invalid teacher'}), 400

        data['teacher_name'] = teacher['name']
        course_id = course_model.create_course(data)
        user_model.assign_course_to_teacher(data['teacher_id'], course_id)

        return jsonify({'message': 'Course created!', 'course_id': course_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses', methods=['GET'])
def get_my_courses():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = user_model.find_by_id(current_user_id)

        if user['role'] == 'admin':
            courses = course_model.get_all_courses()
        elif user['role'] == 'teacher':
            courses = course_model.get_teacher_courses(current_user_id)
        else:
            # For students, get courses from the courses collection directly
            courses = course_model.get_student_courses(current_user_id)

        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/available', methods=['GET'])
def get_available_courses():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_student(current_user_id):
            return jsonify({'error': 'Only students can browse courses'}), 403

        all_courses = course_model.get_all_courses()
        enrolled = course_model.get_student_courses(current_user_id)
        enrolled_ids = {c['_id'] for c in enrolled}
        available = [c for c in all_courses if c['_id'] not in enrolled_ids]

        return jsonify(available), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>', methods=['GET'])
def get_course_by_id(course_id):
    try:
        verify_jwt_in_request()
        course = course_model.get_course_by_id(course_id)
        if course:
            return jsonify(course), 200
        return jsonify({'error': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can update courses'}), 403

        data = request.json
        success = course_model.update_course(course_id, data)
        if success:
            return jsonify({'message': 'Course updated!'}), 200
        return jsonify({'error': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can delete courses'}), 403

        success = course_model.delete_course(course_id)
        if success:
            return jsonify({'message': 'Course deleted!'}), 200
        return jsonify({'error': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>/enroll', methods=['POST'])
def enroll_in_course(course_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_student(current_user_id):
            return jsonify({'error': 'Only students can enroll'}), 403

        # Check if student is blocked
        user = user_model.find_by_id(current_user_id)
        if user.get('is_blocked', False):
            return jsonify({'error': 'Your account has been blocked'}), 403

        # Check if already enrolled (check course's students array)
        course = course_model.get_course_by_id(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        if current_user_id in course.get('students', []):
            return jsonify({'error': 'Already enrolled in this course'}), 400

        # Add student to course AND update user's enrolled_courses
        user_model.enroll_student_in_course(current_user_id, course_id)
        course_model.assign_student(course_id, current_user_id)

        return jsonify({'message': 'Enrolled successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>/materials', methods=['POST'])
def add_material_to_course(course_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        data = request.json

        course = course_model.get_course_by_id(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Admin can add to any course, teacher only to their own
        if is_admin(current_user_id):
            pass
        elif is_teacher(current_user_id):
            if course['teacher_id'] != current_user_id:
                return jsonify({'error': 'Not your course'}), 403
        else:
            return jsonify({'error': 'Access denied'}), 403

        course_model.add_material(course_id, data)
        return jsonify({'message': 'Material added!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>/assignments', methods=['GET'])
def get_course_assignments(course_id):
    try:
        verify_jwt_in_request()
        from models.assignment import Assignment
        assignment_model = Assignment()
        assignments = assignment_model.get_course_assignments(course_id)
        for a in assignments:
            a['_id'] = str(a['_id'])
        return jsonify(assignments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>/quizzes', methods=['GET'])
def get_course_quizzes(course_id):
    try:
        verify_jwt_in_request()
        from models.quiz import Quiz
        quiz_model = Quiz()
        quizzes = quiz_model.get_course_quizzes(course_id)
        for q in quizzes:
            q['_id'] = str(q['_id'])
        return jsonify(quizzes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<course_id>/students', methods=['GET'])
def get_course_students(course_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_teacher(current_user_id) and not is_admin(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        course = course_model.get_course_by_id(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        students = []
        for student_id in course.get('students', []):
            student = user_model.find_by_id(student_id)
            if student:
                students.append({
                    '_id': str(student['_id']),
                    'name': student['name'],
                    'email': student['email'],
                    'is_blocked': student.get('is_blocked', False)
                })

        return jsonify(students), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
