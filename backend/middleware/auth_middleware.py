from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models.user import User
from functools import wraps

user_model = User()

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
    return wrapper

def check_blocked_user():
    """
    Middleware to check if the logged-in user is blocked.
    Called before every request via app.before_request.
    Skips public routes (login, register, static files).
    """
    # Skip public routes that don't need auth
    public_paths = ['/api/auth/login', '/api/auth/register', '/api/auth/logout']
    if request.path in public_paths:
        return None

    # Skip static file routes
    if not request.path.startswith('/api/'):
        return None

    # Skip if no Authorization header (will fail at JWT check in the route)
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = user_model.find_by_id(current_user_id)

        if user and user.get('is_blocked', False):
            return jsonify({
                'error': 'Your account has been blocked. Contact administrator.'
            }), 403
    except Exception:
        # Let the actual route handle JWT errors
        pass

    return None
