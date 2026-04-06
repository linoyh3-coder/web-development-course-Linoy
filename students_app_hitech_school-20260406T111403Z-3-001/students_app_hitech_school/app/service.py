# application logic
import students_app_hitech_school.app.db as db


class ServiceError(Exception): pass


def add_student(student):
    """Add a student to the system. student age must be in the range 18 - 120"""
    if not 18 <= student["age"] <= 120:
        raise ServiceError(f'Student age is out of range: {student["age"]}')

    return db.add_student(student)


def get_students():
    return db.get_students()


def get_student(student_id):
    return db.get_student(student_id)


def update_student(student_update):
    return db.update_student(student_update)


def delete_student(student_id):
    return db.delete_student(student_id)

if __name__=="__main__":
    result = get_student(1)
    print(result)
    result = delete_student(2)
    print(result)