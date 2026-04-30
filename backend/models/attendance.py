from datetime import datetime
from utils.db import MongoDB
from bson import ObjectId

class Attendance:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db['attendance']
    
    def mark_attendance(self, course_id, student_id, status):
        attendance_record = {
            'course_id': course_id,
            'student_id': student_id,
            'date': datetime.utcnow().date().isoformat(),
            'status': status,
            'marked_at': datetime.utcnow()
        }
        
        # Check if attendance already marked for today
        existing = self.collection.find_one({
            'course_id': course_id,
            'student_id': student_id,
            'date': attendance_record['date']
        })
        
        if existing:
            result = self.collection.update_one(
                {'_id': existing['_id']},
                {'$set': {'status': status, 'marked_at': datetime.utcnow()}}
            )
        else:
            result = self.collection.insert_one(attendance_record)
        
        return result.acknowledged
    
    def get_student_attendance(self, student_id, course_id=None):
        query = {'student_id': student_id}
        if course_id:
            query['course_id'] = course_id
        
        return list(self.collection.find(query))
    
    def get_course_attendance(self, course_id):
        return list(self.collection.find({'course_id': course_id}))