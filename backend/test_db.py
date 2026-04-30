from utils.db import MongoDB
from models.user import User
import traceback

def test_connection():
    print("=" * 50)
    print("Testing MongoDB Connection")
    print("=" * 50)
    
    try:
        # Test database connection
        db = MongoDB.get_db()
        print("[OK] Database connection successful!")
        
        # Test user model
        user_model = User()
        
        # Try to create a test user
        test_user = {
            'name': 'Noshaba khan',
            'email': 'noshaba@example.com',
            'password': 'test123',
            'role': 'teacher'
        }
        
        # Check if test user exists
        existing = user_model.find_by_email('noshaba@example.com')
        if not existing:
            user_id = user_model.create_user(test_user)
            print(f"[OK] Test user created with ID: {user_id}")
        else:
            print("[WARN] Test user already exists")
        
        # Try to find user
        user = user_model.find_by_email('test@example.com')
        if user:
            print(f"[OK] User found: {user['name']} ({user['email']})")
        
        # List all users
        all_users = list(user_model.collection.find({}, {'password': 0}))
        print(f"\n📊 Total users in database: {len(all_users)}")
        for u in all_users:
            print(f"   - {u['name']} ({u['email']}) - Role: {u['role']}")
        
        print("\n[OK] All tests passed!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print(traceback.format_exc())

if __name__ == '__main__':
    test_connection()