import pytest
import requests
from students_app_hitech_school.app import db


@pytest.fixture
def base_url():
    # בסיס ה-URL של ה-API לכל הבדיקות
    return "http://127.0.0.1:5000/students"


@pytest.fixture(autouse=True)
def clear_students():
    # מאפס את ה-db לפני כל טסט כדי למנוע תלות בין בדיקות
    db._clear_db()


@pytest.fixture
def add_students(base_url):
    # יוצר מראש 3 תלמידים כדי שיהיה מצב התחלתי קבוע לטסטים
    students = [
        {'age': 21, "name": "Aaa"},
        {'age': 22, "name": "Bbb"},
        {'age': 23, "name": "Ccc"},
    ]

    created_students = []

    # מוסיף כל תלמיד לשרת ושומר את התוצאה (כולל ID שנוצר)
    for student in students:
        res = requests.post(base_url, json=student)
        created_students.append(res.json())

    return created_students


# ================= GET STUDENTS ================= #

def test_get_all_students(base_url, add_students):
    # בדיקה שמחזירה את כל התלמידים הקיימים במערכת
    res = requests.get(base_url)

    assert res.status_code == 200
    assert res.reason == "OK"

    # משווה בין מה שבשרת למה שהוכנס בפיצ'ר
    assert res.json() == add_students


def test_get_one_student_simple(base_url, add_students):
    # בדיקה של שליפת תלמיד לפי ID
    res = requests.get(f"{base_url}/1")

    assert res.status_code == 200
    assert res.reason == "OK"

    # תלמיד ראשון מתוך הרשימה שהוזרקה בפיצ'ר
    assert res.json() == add_students[0]


@pytest.mark.parametrize(
    "s_id",
    [1, 2, 3],
)
def test_get_one_student_v1(base_url, add_students, s_id):
    # בדיקה פרמטרית: שליפת כל תלמיד לפי ID
    res = requests.get(f"{base_url}/{s_id}")

    assert res.status_code == 200
    assert res.reason == "OK"

    # ID מתחיל מ-1 ולכן עושים התאמה לרשימה
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
    # אותו רעיון כמו הקודם אבל עם אינדקס ברור יותר
    res = requests.get(f"{base_url}/{s_id}")

    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json() == add_students[index]


# ================= GET STUDENTS - NEGATIVE ================= #

@pytest.mark.parametrize(
    "s_id",
    [100, 200, 300]
)
def test_get_one_student_negative(base_url, add_students, s_id):
    # בדיקה של ID שלא קיים במערכת
    res = requests.get(f"{base_url}/{s_id}")

    assert res.status_code == 404
    assert res.reason == "NOT FOUND"

    # בדיקה שההודעה תואמת שגיאה של "לא נמצא"
    assert res.json() == {'message': f"'student not found: {s_id}'"}


# ================= ADD STUDENT ================= #

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
    # בדיקה של הוספת תלמיד תקין למערכת
    res = requests.post(base_url, json=student)

    assert res.status_code == 201

    created_student = res.json()

    # בדיקה שהתלמיד שנוצר תואם למה שנשלח
    assert created_student.get("name") == student["name"]
    assert created_student.get("age") == student["age"]
    assert "id" in created_student


@pytest.mark.parametrize(
    "student",
    [
        pytest.param({"name": "AA", "age": 17}, id="too young"),
        pytest.param({"name": "Benny", "age": 121}, id="too old"),
        pytest.param({"name": "A", "age": 25}, id="short name"),
        pytest.param({"name": "", "age": 25}, id="no name"),
    ],
)
def test_add_student_negative(base_url, student):
    # בדיקה של נתונים לא תקינים – אמור להיכשל
    res = requests.post(base_url, json=student)

    assert res.status_code == 400
    assert res.reason == "BAD REQUEST"


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
    # בדיקה משולבת של תקין ולא תקין
    payload = {"name": name, "age": age}

    res = requests.post(base_url, json=payload)

    assert res.status_code == expected_status


# ================= UPDATE STUDENT ================= #

@pytest.mark.xfail(reason="BUG: update endpoint ignores student_id (not RESTFUL)")
@pytest.mark.parametrize(
    "student_id, name, age, expected_status",
    [
        pytest.param(1, "Aaa", 25, 200, id="positive update"),
        pytest.param(2, "Benny", 22, 200, id="positive update second student"),
        pytest.param(1, "Bob Young", 18, 200, id="boundary values"),
        pytest.param(1, "", 17, 400, id="invalid data"),
    ]
)
def test_update_student_mixed(base_url, add_students, student_id, name, age, expected_status):
    # בדיקה של עדכון תלמיד קיים
    payload = {"name": name, "age": age}

    # BUG: ה-API לא תומך ב- /students/<id>
    res = requests.put(f"{base_url}/{student_id}", json=payload)

    assert res.status_code == expected_status

    if expected_status == 200:
        data = res.json()

        # בדיקה שהתלמיד באמת עודכן
        assert data["id"] == student_id
        assert data["name"] == name
        assert data["age"] == age


def test_update_student_effect(base_url, add_students):
    payload = {"id": 1, "name": "Updated student", "age": 25}

    #  PUT
    res = requests.put(base_url, json=payload)
    assert res.status_code == 200

    # בדיקה
    res = requests.get(f"{base_url}/1")
    data = res.json()

    assert data["name"] == "Updated student"
    assert data["age"] == 25


def test_update_non_existing_student(base_url, add_students):
    payload = {"name": "Updated student", "age": 25}
    res = requests.put(f"{base_url}/444", json=payload)
    assert res.status_code == 404


# ================= DELETE STUDENT ================= #

@pytest.mark.parametrize(
    "student_id, expected_status",
    [
        pytest.param(1, 200, id="delete existing student"),
        pytest.param(999, 404, id="delete non-existing student"),
    ]
)
def test_delete_student_mixed(base_url, add_students, student_id, expected_status):
    # בדיקה של מחיקת תלמיד לפי ID
    res = requests.delete(f"{base_url}/{student_id}")

    assert res.status_code == expected_status

    if expected_status == 200:
        # בדיקה שהתלמיד באמת נמחק מהמערכת
        res = requests.get(f"{base_url}/{student_id}")
        assert res.status_code == 404


def test_delete_twice(base_url, add_students):
    requests.delete(f"{base_url}/1")
    res = requests.delete(f"{base_url}/1")

    assert res.status_code ==404


def test_delete_does_not_affect_others(base_url, add_students):
    requests.delete(f"{base_url}/1")
    res = requests.get(base_url)

    assert len(res.json()) == 2

# =============== Flow Tests ================ #

def test_full_flow(base_url):
    # create
    res = requests.post(base_url, json={"name": "Flow", "age": 25})
    assert res.status_code == 201
    student = res.json()
    student_id = student["id"]

    # get
    res = requests.get(f"{base_url}/{student_id}")
    assert res.status_code == 200

    # update
    res = requests.put(
        base_url,
        json={"id": student_id, "name": "Flow2", "age": 30}
    )
    assert res.status_code == 200

    # verify update
    res = requests.get(f"{base_url}/{student_id}")
    assert res.json()["name"] == "Flow2"
    assert res.json()["age"] == 30

    # delete
    res = requests.delete(f"{base_url}/{student_id}")
    assert res.status_code == 200

    # verify delete
    res = requests.get(f"{base_url}/{student_id}")
    assert res.status_code == 404