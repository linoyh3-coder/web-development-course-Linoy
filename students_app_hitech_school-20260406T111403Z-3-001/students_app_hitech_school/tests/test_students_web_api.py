import pytest
import requests
from students_app_hitech_school.app import db


@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000/students"


# זה דואג לנקות את טבלת התלמידים לפני כל אחד מהטסטים במודול
@pytest.fixture(autouse=True)
def clear_students():
    db._clear_db()


# זה מוסיף למערכת שלושה תלמידים ומחזיר אותם לטסטים שצריכים
@pytest.fixture
def add_students(base_url):
    students = [
        {'age': 21, "name": "Aaa"},
        {'age': 22, "name": "Bbb"},
        {'age': 23, "name": "Ccc"},
    ]
    created_students = []
    for student in students:
        res = requests.post(base_url, json=student)
        created_students.append(res.json())
    return created_students


# THE TESTS ==========================================

    # ============== Get Student - Positive Tests ============== #


def test_get_all_students(base_url, add_students):
    res = requests.get(base_url)
    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json() == add_students


def test_get_one_student_simple(base_url, add_students):
    res = requests.get(f"{base_url}/1")
    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json() == add_students[0]


# parameterized test can run with many inputs
@pytest.mark.parametrize(
    "s_id",
    [1, 2, 3],
)
def test_get_one_student_v1(base_url, add_students, s_id):
    res = requests.get(f"{base_url}/{s_id}")
    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json() == add_students[s_id - 1]


@pytest.mark.parametrize(
    "s_id, index",
    [
        [1, 0],
        [2, 1],
        [3, 2],
    ],
    ids=["first student", "second student", "third student"]
)
def test_get_one_student_v2(base_url, add_students, s_id, index):
    res = requests.get(f"{base_url}/{s_id}")
    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json() == add_students[index]


    # ============== Get Student - Negative Tests =============== #

@pytest.mark.parametrize(
    "s_id",
    [100, 200, 300]
)
def test_get_one_student_negative(base_url, add_students, s_id):
    res = requests.get(f"{base_url}/{s_id}")
    assert res.status_code == 404
    assert res.reason == "NOT FOUND"
    assert res.json() == {'message': f'student not found: {s_id}'}



    # ============== Add Student - Positive Tests =============== #

@pytest.mark.parametrize(
    "student",
    [
        {"name": "AA", "age": 18},
        {"name": "Benny", "age": 25},
        {"name": "Robinson Cruso", "age": 120},
    ],
    ids=[
        "minimum value input",
        "average input",
        "high value input",
    ]
)
def test_add_student(base_url, student):
    res = requests.post(base_url, json=student)
    assert res.status_code == 201
    # נבדוק את הערכים של התלמיד שהוספנו ונשווה
    created_student = res.json()
    assert created_student.get("name") == student["name"]
    assert created_student.get("age") == student["age"]
    assert "id" in created_student


    # ============== Add Student - Negative Tests =============== #

@pytest.mark.parametrize(
    "student",
    [
        pytest.param({"name": "AA", "age": 17}, id="too young"),
        pytest.param({"name": "Benny", "age": 121}, id="too old"),
        pytest.param({"name": "A", "age": 25}, id="name too short"),
        pytest.param({"name": "", "age": 25}, id="no name"),
    ],
)
def test_add_student_negative(base_url, student):
    res = requests.post(base_url, json=student)
    assert res.status_code == 400
    assert res.reason == "BAD REQUEST"


    # ============== Add Student - Mixed Tests =============== #

@pytest.mark.parametrize(
    "name, age, expected_status",
    [
        pytest.param("Danny", 25, 201, id="positive average input"),
        pytest.param("Aa", 18, 201, id="positive low value input"),
        pytest.param("", 18, 400, id="negative no name"),
        pytest.param("Ann", 121, 400, id="negative too old"),
    ]
)
def test_add_student_mixed(base_url, name, age, expected_status):
    payload = {"name": name, "age": age}
    res = requests.post(base_url, json=payload)
    assert res.status_code == expected_status


    # ============== Update Student - Mixed Tests =============== #

@pytest.mark.parametrize(
    "name, age, expected_status",
    [
        pytest.param("Aaa", 25, 201, id="positive age input"),
        pytest.param("Benny", 22, 201, id="positive name input"),
        pytest.param("Bob Young", 18, 201, id="positive low value input"),
        pytest.param("", 17, 400, id="negative too young"),
    ]
)
def test_update_student_mixed(base_url, name, age, expected_status):
    payload = {"name": name, "age": age}
    res = requests.post(base_url, json=payload)

    assert res.status_code == expected_status

    if expected_status == 201:
        data = res.json()
        assert data["name"] == name
        assert data["age"] == age
        assert "id" in data


    # ============== Delete Student - Tests =============== #

@pytest.mark.parametrize(
    "student_id, expected_status",
    [
        pytest.param(1, 200, id="delete existing student"),
        pytest.param(999, 404, id="delete non-existing student"),
    ]
)
def test_delete_student_mixed(base_url, add_students, student_id, expected_status):
    res = requests.delete(f"{base_url}/{student_id}")
    assert res.status_code == expected_status

    if expected_status == 200:
        # לוודא שבאמת נמחק
        res = requests.get(f"{base_url}/{student_id}")
        assert res.status_code == 404
