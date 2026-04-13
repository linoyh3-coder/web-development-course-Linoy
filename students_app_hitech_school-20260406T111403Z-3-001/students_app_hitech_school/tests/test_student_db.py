# test_student_db_only.py
import pytest
from pymysql import DataError

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

def test_add_student_valid():
    student = {"name": "DB User", "age": 18}
    added = add_student(student)
    assert "id" in added
    assert added ["name"] == "DB User"
    assert added ["age"] == 18
    delete_student(added["id"])

def test_add_student_max_age():
    student = {"name": "DB User", "age": 120}
    added = add_student(student)
    assert "id" in added
    assert added["name"] == "DB User"
    assert added["age"] == 120
    delete_student(added["id"])

def test_add_student_short_name():
    student = {"name": "DB", "age": 45}
    added = add_student(student)
    assert "id" in added
    assert added["name"] == "DB"
    assert added["age"] == 45
    delete_student(added["id"])

def test_add_student_missing_age():
    with pytest.raises(KeyError):
        add_student({"name": "No Age"})

def test_age_not_number():
    with pytest.raises(DataError):
        add_student({"name": "DB", "age": "twenty"})



# ----------------- READ TESTS ----------------- #
def test_get_students_db(sample_student):
    students = get_students()
    assert any(s["id"] == sample_student["id"] for s in students)

def test_get_student_positive_db(sample_student):
    fetched = get_student(sample_student["id"])
    assert fetched["name"] == sample_student["name"]
    assert fetched["age"] == sample_student["age"]

def test_get_student_negative_db():
    with pytest.raises(KeyError):
        get_student(999999)

def test_get_none():
    with pytest.raises(KeyError):
        get_student(None)

def test_get_string_id():
    with pytest.raises(KeyError):
        get_student("123")



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

def test_update_only_id(sample_student):
    with pytest.raises(KeyError):
        update_student({"id": sample_student["id"]})




# ----------------- DELETE TESTS ----------------- #
def test_delete_student_positive_db():
    student = add_student({"name": "PyTest User", "age": 35})
    deleted = delete_student(student["id"])
    assert deleted["id"] == student["id"]

    with pytest.raises(KeyError):
        get_student(student["id"])

def test_delete_student_negative_db():
    with pytest.raises(KeyError):
        delete_student(999999)

def test_double_delete():
    student = add_student({"name": "PyTest User", "age": 63})
    delete_student(student["id"])

    with pytest.raises(KeyError):
        delete_student(student["id"])

def test_update_after_delete():
    student = add_student({"name": "PyTest User", "age": 63})
    delete_student(student["id"])

    with pytest.raises(KeyError):
        update_student(student)



# ----------------- Functional TESTS ----------------- #

def test_db_consistency_after_add():
    student = add_student({"name": "PyTest User", "age": 35})
    students = get_students()
    assert any(s["id"] == student["id"] for s in students)
    delete_student(student["id"])


def test_unique_ids():
    s1 = add_student({"name": "A", "age": 20})
    s2 = add_student({"name": "B", "age": 21})

    assert s1["id"] != s2["id"]

    delete_student(s1["id"])
    delete_student(s2["id"])

def test_db_after_delete():
    student = add_student({"name": "Temp", "age": 30})
    delete_student(student["id"])

    students = get_students()
    assert not any(s["id"] == student["id"] for s in students)

def test_full_functionality():
    student = add_student({"name": "Temp", "age": 30})

    updated = update_student({
        "id" : student["id"],
        "name" : "Ben",
        "age" : 24
    })

    delete_student(updated["id"])

    with pytest.raises(KeyError):
        get_student(updated["id"])


