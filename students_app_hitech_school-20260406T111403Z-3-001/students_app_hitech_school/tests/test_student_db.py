import pytest
from students_app_hitech_school.app import db


# ================= FIXTURES ================= #

@pytest.fixture(autouse=True)
def clear_db():
    """
    מאפס את ה-DB לפני כל טסט
    """
    db._clear_db()


@pytest.fixture
def sample_student():
    """
    יוצר תלמיד אחד בסיסי לכל טסט שצריך
    ומנקה אותו בסוף הטסט
    """
    student = db.add_student({"name": "PyTest User", "age": 25})

    yield student

    try:
        db.delete_student(student["id"])
    except Exception:
        pass


# ================= CREATE ================= #

@pytest.mark.parametrize(
    "student",
    [
        pytest.param({"name": "A", "age": 20}, id="min valid"),
        pytest.param({"name": "B", "age": 120}, id="max age"),
        pytest.param({"name": "Long Name", "age": 30}, id="normal"),
    ]
)
def test_add_student_valid(student):
    added = db.add_student(student.copy())

    assert "id" in added
    assert added["name"] == student["name"]
    assert added["age"] == student["age"]


@pytest.mark.parametrize(
    "student",
    [
        pytest.param({"name": "A", "age": "twenty"}, id="invalid age"),
        pytest.param({"name": "A"}, id="missing age"),
    ]
)
def test_add_student_invalid(student):
    with pytest.raises(Exception):
        db.add_student(student)


# ================= READ ================= #

def test_get_student(sample_student):
    result = db.get_student(sample_student["id"])

    assert result == sample_student


@pytest.mark.parametrize("bad_id", [999, None, "123"])
def test_get_student_negative(bad_id):
    with pytest.raises(Exception):
        db.get_student(bad_id)


# ================= UPDATE ================= #

def test_update_student(sample_student):
    updated = db.update_student({
        "id": sample_student["id"],
        "name": "Updated",
        "age": 30
    })

    assert updated["id"] == sample_student["id"]
    assert updated["name"] == "Updated"
    assert updated["age"] == 30


def test_update_non_existing():
    with pytest.raises(Exception):
        db.update_student({"id": 999, "name": "X", "age": 20})


# ================= DELETE ================= #

def test_delete_student(sample_student):
    deleted = db.delete_student(sample_student["id"])

    assert deleted["id"] == sample_student["id"]

    with pytest.raises(Exception):
        db.get_student(sample_student["id"])


@pytest.mark.parametrize("bad_id", [999, -1])
def test_delete_negative(bad_id):
    with pytest.raises(Exception):
        db.delete_student(bad_id)


# ================= FULL FLOW ================= #

def test_full_flow():
    # CREATE
    student = db.add_student({"name": "Flow", "age": 22})

    # UPDATE
    updated = db.update_student({
        "id": student["id"],
        "name": "Flow Updated",
        "age": 23
    })

    assert updated["name"] == "Flow Updated"
    assert updated["age"] == 23

    # DELETE
    db.delete_student(updated["id"])

    # VERIFY DELETE
    with pytest.raises(Exception):
        db.get_student(updated["id"])