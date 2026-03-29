# application logic
import app.db as db


class ServiceError(Exception): pass


def add_student(student):
    """Add a student - legal student age is in the range 18 - 120"""
    validate_student(student)
    return db.add_student(student)


def get_students():
    return db.get_students()


def get_student(student_id):
    return db.get_student(student_id)


def update_student(student):
    """Update a student"""
    validate_student(student)
    return db.update_student(student)


def delete_student(student_id):
    return db.delete_student(student_id)


def validate_student(student):
    """raise ServiceError if student ilegal.
    legal student age is in the range 18 - 120.
    Student must have a name with minimum length of 1 letter"""
    if not 18 <= student["age"] <= 120:
        raise ServiceError(f'Student age is illegal: {student["age"]}')
    if not student["name"] or len(student["name"]) == 0:
        raise ServiceError(f'Student name is illegal: {student["name"]}')
