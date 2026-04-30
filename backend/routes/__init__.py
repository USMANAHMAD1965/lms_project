from .auth import auth_bp
from .courses import courses_bp
from .assignments import assignments_bp
from .quizzes import quizzes_bp
from .attendance import attendance_bp

__all__ = ['auth_bp', 'courses_bp', 'assignments_bp', 'quizzes_bp', 'attendance_bp']