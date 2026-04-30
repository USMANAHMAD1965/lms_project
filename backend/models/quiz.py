from datetime import datetime
from backend.utils.db import MongoDB
from bson import ObjectId

class Quiz:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db['quizzes']
    
    def create_quiz(self, quiz_data):
        quiz = {
            'course_id': quiz_data['course_id'],
            'title': quiz_data['title'],
            'questions': quiz_data.get('questions', []),
            'duration': quiz_data['duration'],
            'total_marks': quiz_data['total_marks'],
            'due_date': quiz_data.get('due_date'),
            'attempts': [],
            'created_at': datetime.utcnow()
        }
        result = self.collection.insert_one(quiz)
        return str(result.inserted_id)
    
    def attempt_quiz(self, quiz_id, student_id, answers):
        attempt = {
            'student_id': student_id,
            'answers': answers,
            'attempted_at': datetime.utcnow(),
            'marks_obtained': 0,
            'graded': False
        }
        result = self.collection.update_one(
            {'_id': ObjectId(quiz_id)},
            {'$push': {'attempts': attempt}}
        )
        return result.modified_count > 0
    
    def grade_quiz(self, quiz_id, student_id, marks):
        result = self.collection.update_one(
            {
                '_id': ObjectId(quiz_id),
                'attempts.student_id': student_id
            },
            {
                '$set': {
                    'attempts.$.marks_obtained': marks,
                    'attempts.$.graded': True
                }
            }
        )
        return result.modified_count > 0
    
    def get_course_quizzes(self, course_id):
        return list(self.collection.find({'course_id': course_id}))
    
    def get_student_attempts(self, student_id):
        return list(self.collection.find({'attempts.student_id': student_id}))