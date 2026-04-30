from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client = None
    db = None
    
    @classmethod
    def connect(cls):
        try:
            if cls.client is None:
                # Get MongoDB URI from environment
                mongo_uri = os.getenv('MONGODB_URI')
                
                if not mongo_uri:
                    raise ValueError("MONGODB_URI not found in environment variables")
                
                print(f"Connecting to MongoDB Atlas...")
                
                # Connect with timeout
                cls.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                
                # Test connection
                cls.client.admin.command('ping')
                
                cls.db = cls.client['lms_db']
                print("[OK] Connected to MongoDB Atlas successfully!")
                
                # Create indexes for better performance
                cls.create_indexes()
                
        except ConnectionFailure as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            print(f"[ERROR] Server selection timeout: {e}")
            raise
        except Exception as e:
            print(f"[ERROR] MongoDB connection error: {e}")
            raise
    
    @classmethod
    def create_indexes(cls):
        """Create indexes for better query performance"""
        try:
            # Users collection indexes
            cls.db.users.create_index("email", unique=True)
            
            # Courses collection indexes
            cls.db.courses.create_index("teacher_id")
            cls.db.courses.create_index("students")
            
            # Assignments collection indexes
            cls.db.assignments.create_index("course_id")
            
            # Quizzes collection indexes
            cls.db.quizzes.create_index("course_id")
            
            # Attendance collection indexes
            cls.db.attendance.create_index([("course_id", 1), ("student_id", 1), ("date", 1)])
            
            print("[OK] Database indexes created successfully!")
        except Exception as e:
            print(f"[WARN] Warning: Could not create indexes: {e}")
    
    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect()
        return cls.db
    
    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")