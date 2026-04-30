from datetime import datetime
from backend.utils.db import MongoDB
from backend.models.user import User
import bcrypt

def create_admin():
    # Connect to database
    MongoDB.connect()
    user_model = User()

    # Check if admin exists
    admin = user_model.find_by_email('admin@learnhub.com')

    if not admin:
        # Hash password
        password = 'admin123'
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        admin_data = {
            'name': 'System Administrator',
            'email': 'admin@learnhub.com',
            'password': hashed_password,
            'role': 'admin',
            'is_blocked': False,
            'assigned_courses': [],
            'enrolled_courses': [],
            'bio': 'System Administrator',
            'profile_pic': '',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = user_model.collection.insert_one(admin_data)
        print(f"[OK] Admin created successfully!")
        print(f"Email: admin@learnhub.com")
        print(f"Password: admin123")
        print(f"Admin ID: {result.inserted_id}")
    else:
        print("[OK] Admin already exists!")
        print(f"Email: {admin['email']}")
        print(f"Name: {admin['name']}")

if __name__ == '__main__':
    create_admin()
