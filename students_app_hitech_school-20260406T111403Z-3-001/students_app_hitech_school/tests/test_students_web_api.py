import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/students"


# =========================
# Fixtures
# =========================

@pytest.fixture
def new_student():
    data = {"name": "Fixture Student", "age": 20}
    response = requests.post(BASE_URL, json=data)
    assert response.status_code == 201
    return response.json()



def test_student_types(new_student):
    assert isinstance(new_student["id"], int)
    assert isinstance(new_student["name"], str)
    assert isinstance(new_student["age"], int)


# =========================
# GET student by ID
# =========================

def test_get_student_positive(new_student):
    student_id = new_student["id"]

    response = requests.get(f"{BASE_URL}/{student_id}")
    assert response.status_code == 200


def test_get_student_response_structure(new_student):
    response = requests.get(f"{BASE_URL}/{new_student['id']}")
    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "age" in data


def test_get_student_not_found():
    response = requests.get(f"{BASE_URL}/999999")
    assert response.status_code == 404


def test_get_student_string_id():
    response = requests.get(f"{BASE_URL}/abc")
    assert response.status_code == 404  # Flask behavior


def test_get_student_negative_id():
    response = requests.get(f"{BASE_URL}/-1")
    assert response.status_code == 404


# =========================
# GET all students
# =========================

def test_get_all_students():
    response = requests.get(BASE_URL)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# =========================
# POST add student
# =========================

def test_add_student_valid():
    data = {"name": "API Student", "age": 25}
    response = requests.post(BASE_URL, json=data)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "API Student"


def test_add_student_empty_body():
    response = requests.post(BASE_URL, json={})
    assert response.status_code == 500


def test_unique_ids():
    s1 = requests.post(BASE_URL,json={"name": "A", "age": 20}).json()
    s2 = requests.post(BASE_URL, json={"name": "B", "age": 22}).json()

    assert s1["id"] != s2["id"]


def test_add_student_none():
    response = requests.post(BASE_URL, json=None)
    assert response.status_code in [400, 415]


def test_add_student_invalid_json():
    response = requests.post(BASE_URL, data="not json")
    assert response.status_code in [400, 415]


# =========================
# FLOW: create + get
# =========================

def test_create_and_get_student():
    data = {"name": "Flow Test", "age": 22}
    create_res = requests.post(BASE_URL, json=data)

    assert create_res.status_code == 201
    student = create_res.json()

    get_res = requests.get(f"{BASE_URL}/{student['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Flow Test"


# =========================
# PUT update student
# =========================

def test_update_student_positive(new_student):
    update_data = {
        "id": new_student["id"],
        "name": "Updated",
        "age": 30
    }

    response = requests.put(BASE_URL, json=update_data)
    assert response.status_code == 200


def test_update_and_verify(new_student):
    update_data = {
        "id": new_student["id"],
        "name": "NewName",
        "age": 30
    }

    requests.put(BASE_URL, json=update_data)

    get_res = requests.get(f"{BASE_URL}/{new_student['id']}")
    assert get_res.json()["name"] == "NewName"


def test_update_empty_body():
    response = requests.put(BASE_URL, json={})
    assert response.status_code in [400, 404]


# =========================
# DELETE student
# =========================

def test_delete_student_positive(new_student):
    student_id = new_student["id"]

    response = requests.delete(f"{BASE_URL}/{student_id}")
    assert response.status_code == 200


def test_delete_and_verify(new_student):
    student_id = new_student["id"]

    requests.delete(f"{BASE_URL}/{student_id}")
    get_res = requests.get(f"{BASE_URL}/{student_id}")

    assert get_res.status_code == 404


def test_delete_student_invalid():
    response = requests.delete(f"{BASE_URL}/-1")
    assert response.status_code == 404
