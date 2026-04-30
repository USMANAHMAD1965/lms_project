from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from models.user import User
import datetime
import traceback

auth_bp = Blueprint('auth', __name__)
user_model = User()

# Helper function to check admin role
def is_admin(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'admin'

# Helper function to check teacher role
def is_teacher(user_id):
    user = user_model.find_by_id(user_id)
    return user and user.get('role') == 'teacher'

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        print(f"[*] Registration attempt: {data.get('email')}")
        
        # Only allow student registration
        if data.get('role') in ['admin', 'teacher']:
            return jsonify({'error': 'Admin and Teacher accounts can only be created by administrator'}), 403
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user exists
        existing_user = user_model.find_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = user_model.create_user(data)
        print(f"[OK] User created: {data['email']}")
        
        return jsonify({
            'message': 'Registration successful! Please login.',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Registration error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/create-user', methods=['POST'])
def admin_create_user():
    try:
        # Get token and verify
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        # Check if admin
        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can create users'}), 403
        
        data = request.json
        print(f"[*] Admin creating user: {data.get('email')}")
        
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        existing_user = user_model.find_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        user_id = user_model.create_user(data)
        
        return jsonify({
            'message': f'{data["role"].capitalize()} created successfully!',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Admin create user error: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        print(f"[*] Login attempt: {data.get('email')}")
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = user_model.verify_password(data['email'], data['password'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user.get('is_blocked', False):
            return jsonify({'error': 'Your account has been blocked'}), 403
        
        access_token = create_access_token(
            identity=str(user['_id']),
            expires_delta=datetime.timedelta(days=1)
        )
        
        print(f"[OK] Login successful: {data['email']}")
        
        return jsonify({
            'message': 'Login successful!',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        user = user_model.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'bio': user.get('bio', ''),
            'profile_pic': user.get('profile_pic', ''),
            'created_at': user['created_at']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        data = request.json
        
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'bio' in data:
            update_data['bio'] = data['bio']
        
        success = user_model.update_profile(current_user_id, update_data)
        
        if success:
            return jsonify({'message': 'Profile updated successfully!'}), 200
        return jsonify({'error': 'Failed to update profile'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can view all users'}), 403
        
        role = request.args.get('role')
        users = user_model.get_all_users(role)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>', methods=['PUT'])
def admin_update_user(user_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can update users'}), 403

        data = request.json
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'email' in data:
            # Check email not taken by another user
            existing = user_model.find_by_email(data['email'])
            if existing and str(existing['_id']) != user_id:
                return jsonify({'error': 'Email already in use by another user'}), 400
            update_data['email'] = data['email']
        if 'role' in data:
            update_data['role'] = data['role']

        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400

        success = user_model.update_profile(user_id, update_data)
        if success:
            return jsonify({'message': 'User updated successfully!'}), 200
        return jsonify({'error': 'User not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        from bson import ObjectId
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        if not is_admin(current_user_id):
            return jsonify({'error': 'Only admin can delete users'}), 403
        
        result = user_model.collection.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'User deleted successfully!'}), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>/block', methods=['PUT'])
def block_user(user_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id) and not is_teacher(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        # Teachers can only block students in their courses
        if is_teacher(current_user_id):
            target_user = user_model.find_by_id(user_id)
            if not target_user or target_user.get('role') != 'student':
                return jsonify({'error': 'Teachers can only block students'}), 403
            from models.course import Course
            course_model = Course()
            teacher_courses = course_model.get_teacher_courses(current_user_id)
            student_in_course = any(user_id in c.get('students', []) for c in teacher_courses)
            if not student_in_course:
                return jsonify({'error': 'Student is not in your courses'}), 403

        success = user_model.block_user(user_id)
        if success:
            return jsonify({'message': 'User blocked successfully!'}), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>/unblock', methods=['PUT'])
def unblock_user(user_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not is_admin(current_user_id) and not is_teacher(current_user_id):
            return jsonify({'error': 'Access denied'}), 403

        # Teachers can only unblock students in their courses
        if is_teacher(current_user_id):
            target_user = user_model.find_by_id(user_id)
            if not target_user or target_user.get('role') != 'student':
                return jsonify({'error': 'Teachers can only unblock students'}), 403
            from models.course import Course
            course_model = Course()
            teacher_courses = course_model.get_teacher_courses(current_user_id)
            student_in_course = any(user_id in c.get('students', []) for c in teacher_courses)
            if not student_in_course:
                return jsonify({'error': 'Student is not in your courses'}), 403

        success = user_model.unblock_user(user_id)
        if success:
            return jsonify({'message': 'User unblocked successfully!'}), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful!'}), 200