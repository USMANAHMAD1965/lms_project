from datetime import datetime
from utils.db import MongoDB
from bson import ObjectId

class Course:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db['courses']
    
    def create_course(self, course_data):
        course = {
            'title': course_data['title'],
            'description': course_data['description'],
            'code': course_data.get('code', ''),
            'teacher_id': course_data['teacher_id'],
            'teacher_name': course_data.get('teacher_name', ''),
            'students': course_data.get('students', []),
            'materials': [],
            'assignments': [],
            'quizzes': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = self.collection.insert_one(course)
        return str(result.inserted_id)
    
    def get_all_courses(self):
        courses = list(self.collection.find())
        for course in courses:
            course['_id'] = str(course['_id'])
            if 'teacher_id' in course:
                course['teacher_id'] = str(course['teacher_id'])
        return courses
    
    def get_course_by_id(self, course_id):
        course = self.collection.find_one({'_id': ObjectId(course_id)})
        if course:
            course['_id'] = str(course['_id'])
        return course
    
    def get_teacher_courses(self, teacher_id):
        courses = list(self.collection.find({'teacher_id': teacher_id}))
        for course in courses:
            course['_id'] = str(course['_id'])
        return courses
    
    def get_student_courses(self, student_id):
        courses = list(self.collection.find({'students': student_id}))
        for course in courses:
            course['_id'] = str(course['_id'])
        return courses
    
    def update_course(self, course_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(course_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_course(self, course_id):
        result = self.collection.delete_one({'_id': ObjectId(course_id)})
        return result.deleted_count > 0
    
    def assign_student(self, course_id, student_id):
        result = self.collection.update_one(
            {'_id': ObjectId(course_id)},
            {'$addToSet': {'students': student_id}}
        )
        return result.modified_count > 0
    
    def remove_student(self, course_id, student_id):
        result = self.collection.update_one(
            {'_id': ObjectId(course_id)},
            {'$pull': {'students': student_id}}
        )
        return result.modified_count > 0
    
    def add_material(self, course_id, material_data):
        material = {
            'title': material_data['title'],
            'content': material_data['content'],
            'type': material_data['type'],
            'file_url': material_data.get('file_url', ''),
            'uploaded_at': datetime.utcnow()
        }
        result = self.collection.update_one(
            {'_id': ObjectId(course_id)},
            {'$push': {'materials': material}}
        )
        return result.modified_count > 0