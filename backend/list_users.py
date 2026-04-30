from utils.db import MongoDB
from models.user import User

# Connect to database
db = MongoDB.get_db()
user_model = User()

# Get all users
users = list(user_model.collection.find({}, {'password': 0}))
print(f"\n📊 Total users in database: {len(users)}")
print("=" * 50)
for user in users:
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Blocked: {user.get('is_blocked', False)}")
    print("-" * 30)