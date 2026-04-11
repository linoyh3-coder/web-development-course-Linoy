# test_student_db_only.py
import pytest
from students_app_hitech_school.app.db import (
    get_students,
    add_student,
    get_student,
    update_student,
    delete_student
)

# ----------------- FIXTURE ----------------- #
@pytest.fixture(scope="function")
def sample_student():
    """
    יוצר תלמיד לדוגמה לפני כל בדיקה ומוחק אותו לאחר מכן.
    """
    student = {"name": "PyTest User", "age": 25}
    added = add_student(student)
    yield added
    try:
        delete_student(added["id"])
    except KeyError:
        pass

# ----------------- CREATE TESTS ----------------- #
def test_add_student_db():
    student = {"name": "DB User", "age": 30}
    added = add_student(student)
    assert "id" in added
    assert added["name"] == "DB User"
    # ניקוי אחרי הבדיקה
    delete_student(added["id"])

# ----------------- READ TESTS ----------------- #
def test_get_students_db(sample_student):
    students = get_students()
    assert any(s["id"] == sample_student["id"] for s in students)

def test_get_student_positive_db(sample_student):
    fetched = get_student(sample_student["id"])
    assert fetched["name"] == sample_student["name"]

def test_get_student_negative_db():
    with pytest.raises(KeyError):
        get_student(999999)

# ----------------- UPDATE TESTS ----------------- #
def test_update_student_positive_db(sample_student):
    sample_student["name"] = "PyTest User"
    sample_student["age"] = 28
    updated = update_student(sample_student)
    assert updated["name"] == "PyTest User"
    assert updated["age"] == 28

def test_update_student_negative_db():
    with pytest.raises(KeyError):
        update_student({"id": 999999, "name": "PyTest User", "age": 50})

# ----------------- DELETE TESTS ----------------- #
def test_delete_student_positive_db():
    student = add_student({"name": "PyTest User", "age": 35})
    deleted = delete_student(student["id"])
    assert deleted["id"] == student["id"]
    # ודא שהטוען נמחק באמת
    with pytest.raises(KeyError):
        get_student(student["id"])

def test_delete_student_negative_db():
    with pytest.raises(KeyError):
        delete_student(999999)