from datetime import datetime
from utils.db import MongoDB
from bson import ObjectId
import bcrypt
import traceback

class User:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db['users']
        print("[OK] User model initialized")
    
    def create_user(self, user_data):
        try:
            # Hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt)
            
            user = {
                'name': user_data['name'],
                'email': user_data['email'],
                'password': hashed_password,
                'role': user_data.get('role', 'student'),
                'is_blocked': False,
                'enrolled_courses': [],
                'assigned_courses': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'profile_pic': user_data.get('profile_pic', ''),
                'bio': user_data.get('bio', '')
            }
            
            print(f"[*] Inserting user: {user['email']}")
            result = self.collection.insert_one(user)
            print(f"[OK] User inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"[ERROR] Error creating user: {e}")
            print(traceback.format_exc())
            raise
    
    def find_by_email(self, email):
        try:
            print(f"[*] Searching for user by email: {email}")
            user = self.collection.find_one({'email': email})
            if user:
                print(f"[OK] User found: {email}")
            else:
                print(f"[WARN] User not found: {email}")
            return user
        except Exception as e:
            print(f"[ERROR] Error finding user: {e}")
            return None
    
    def find_by_id(self, user_id):
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            return user
        except Exception as e:
            print(f"[ERROR] Error finding user by ID: {e}")
            return None
    
    def verify_password(self, email, password):
        try:
            user = self.find_by_email(email)
            if user:
                print(f"[*] Verifying password for: {email}")
                if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    print(f"[OK] Password verified for: {email}")
                    return user
                else:
                    print(f"[ERROR] Invalid password for: {email}")
            return None
        except Exception as e:
            print(f"[ERROR] Error verifying password: {e}")
            return None
    
    def update_profile(self, user_id, update_data):
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error updating profile: {e}")
            return False
    
    def block_user(self, user_id):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_blocked': True, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error blocking user: {e}")
            return False
    
    def unblock_user(self, user_id):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_blocked': False, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error unblocking user: {e}")
            return False

    def get_all_users(self, role=None):
        try:
            query = {}
            if role:
                query['role'] = role
            users = list(self.collection.find(query))
            for user in users:
                user['_id'] = str(user['_id'])
                user.pop('password', None)
            return users
        except Exception as e:
            print(f"[ERROR] Error getting all users: {e}")
            return []

    def assign_course_to_teacher(self, teacher_id, course_id):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(teacher_id)},
                {
                    '$addToSet': {'assigned_courses': course_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error assigning course to teacher: {e}")
            return False

    def enroll_student_in_course(self, student_id, course_id):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(student_id)},
                {
                    '$addToSet': {'enrolled_courses': course_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error enrolling student: {e}")
            return False

    def delete_user(self, user_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"[ERROR] Error deleting user: {e}")
            return False