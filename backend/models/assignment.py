from datetime import datetime
from utils.db import MongoDB
from bson import ObjectId

class Assignment:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db['assignments']
    
    def create_assignment(self, assignment_data):
        assignment = {
            'course_id': assignment_data['course_id'],
            'title': assignment_data['title'],
            'description': assignment_data['description'],
            'due_date': assignment_data['due_date'],
            'total_marks': assignment_data['total_marks'],
            'submissions': [],
            'created_at': datetime.utcnow()
        }
        result = self.collection.insert_one(assignment)
        return str(result.inserted_id)
    
    def submit_assignment(self, assignment_id, student_id, submission_data):
        submission = {
            'student_id': student_id,
            'submission_text': submission_data['submission_text'],
            'file_url': submission_data.get('file_url', ''),
            'submitted_at': datetime.utcnow(),
            'marks': None,
            'feedback': ''
        }
        result = self.collection.update_one(
            {'_id': ObjectId(assignment_id)},
            {'$push': {'submissions': submission}}
        )
        return result.modified_count > 0
    
    def grade_assignment(self, assignment_id, student_id, marks, feedback):
        result = self.collection.update_one(
            {
                '_id': ObjectId(assignment_id),
                'submissions.student_id': student_id
            },
            {
                '$set': {
                    'submissions.$.marks': marks,
                    'submissions.$.feedback': feedback
                }
            }
        )
        return result.modified_count > 0
    
    def get_course_assignments(self, course_id):
        return list(self.collection.find({'course_id': course_id}))
    
    def get_student_submissions(self, student_id):
        return list(self.collection.find({'submissions.student_id': student_id}))