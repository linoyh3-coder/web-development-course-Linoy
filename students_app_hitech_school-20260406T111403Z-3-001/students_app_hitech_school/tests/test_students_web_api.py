import pytest
import requests


@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000/students"


@pytest.fixture
def add_students(base_url):
    students = [
        {"age": 21, "name": "Aaa"},
        {"age": 22, "name": "Bbb"},
        {"age": 23, "name": "Ccc"},
    ]

    created = []
    for s in students:
        res = requests.post(base_url, json=s)
        assert res.status_code == 201
        created.append(res.json())

    return created


# =========================
# GET ALL
# =========================

def test_get_all_students(base_url, add_students):
    res = requests.get(base_url)

    assert res.status_code == 200
    assert res.reason == "OK"

    result = res.json()

    assert len(result) >= len(add_students)

    returned_ids = {s["id"] for s in result}
    expected_ids = {s["id"] for s in add_students}

    assert expected_ids.issubset(returned_ids)


# =========================
# GET ONE STUDENT
# =========================

def test_get_one_student_simple(base_url, add_students):
    student = add_students[0]

    res = requests.get(f"{base_url}/{student['id']}")

    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.json()["id"] == student["id"]
    assert res.json()["name"] == student["name"]


@pytest.mark.parametrize("index", [0, 1, 2])
def test_get_one_student_v1(base_url, add_students, index):
    student = add_students[index]

    res = requests.get(f"{base_url}/{student['id']}")

    assert res.status_code == 200
    assert res.json()["id"] == student["id"]


@pytest.mark.parametrize(
    "index",
    [0, 1, 2],
    ids=["first", "second", "third"]
)
def test_get_one_student_v2(base_url, add_students, index):
    student = add_students[index]

    res = requests.get(f"{base_url}/{student['id']}")

    assert res.status_code == 200
    assert res.json()["name"] == student["name"]


# =========================
# NEGATIVE GET
# =========================

@pytest.mark.parametrize("s_id", [999999, -1, "abc"])
def test_get_one_student_negative(base_url, add_students, s_id):
    res = requests.get(f"{base_url}/{s_id}")
    assert res.status_code == 404


# =========================
# ADD STUDENT
# =========================

@pytest.mark.parametrize(
    "student",
    [
        {"name": "AA", "age": 18},
        {"name": "Benny", "age": 25},
        {"name": "Robinson Cruso", "age": 120},
    ],
    ids=["min input", "normal input", "max input"]
)
def test_add_student(base_url, student):
    res = requests.post(base_url, json=student)

    assert res.status_code == 201

    created = res.json()
    assert created["name"] == student["name"]
    assert created["age"] == student["age"]
    assert "id" in created


@pytest.mark.parametrize(
    "student",
    [
        pytest.param({"name": "AA", "age": 17}, id="too young"),
        pytest.param({"name": "Benny", "age": 121}, id="too old"),
        pytest.param({"name": "A", "age": 25}, id="name too short"),
        pytest.param({"name": "", "age": 25}, id="empty name"),
    ],
)
def test_add_student_negative(base_url, student):
    res = requests.post(base_url, json=student)
    assert res.status_code == 400


@pytest.mark.parametrize(
    "name, age, expected_status",
    [
        ("Danny", 25, 201),
        ("Aa", 18, 201),
        ("", 18, 400),
        ("Ann", 121, 400),
    ],
)
def test_add_student_mixed(base_url, name, age, expected_status):
    res = requests.post(base_url, json={"name": name, "age": age})
    assert res.status_code == expected_status


def test_add_student_invalid_json(base_url):
    res = requests.post(base_url, data="not json")
    assert res.status_code in [400, 415]


# =========================
# UNIQUE IDS
# =========================

def test_unique_ids(base_url):
    s1 = requests.post(base_url, json={"name": "A", "age": 20}).json()
    s2 = requests.post(base_url, json={"name": "B", "age": 22}).json()

    assert s1["id"] != s2["id"]


# =========================
# FLOW TEST
# =========================

def test_create_and_get_student(base_url):
    res = requests.post(base_url, json={"name": "Flow Test", "age": 22})
    assert res.status_code == 201

    student = res.json()

    get_res = requests.get(f"{base_url}/{student['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Flow Test"


# =========================
# UPDATE
# =========================

def test_update_and_verify(base_url, add_students):
    student = add_students[0]

    requests.put(
        base_url,
        json={"id": student["id"], "name": "Updated", "age": 30}
    )

    res = requests.get(f"{base_url}/{student['id']}")
    assert res.json()["name"] == "Updated"


def test_update_non_existing(base_url):
    res = requests.put(
        base_url,
        json={"id": 999999, "name": "Test", "age": 35}
    )

    assert res.status_code == 404


def test_update_empty_body(base_url):
    res = requests.put(base_url, json={})
    assert res.status_code in [400, 404]


# =========================
# DELETE
# =========================

def test_delete_student(base_url, add_students):
    student = add_students[0]

    res = requests.delete(f"{base_url}/{student['id']}")
    assert res.status_code == 200


def test_delete_twice(base_url, add_students):
    student = add_students[0]

    r1 = requests.delete(f"{base_url}/{student['id']}")
    r2 = requests.delete(f"{base_url}/{student['id']}")

    assert r1.status_code == 200
    assert r2.status_code == 404


def test_delete_and_verify(base_url, add_students):
    student = add_students[0]

    requests.delete(f"{base_url}/{student['id']}")

    res = requests.get(f"{base_url}/{student['id']}")
    assert res.status_code == 404


def test_delete_invalid(base_url):
    res = requests.delete(f"{base_url}/-1")
    assert res.status_code == 404


# =========================
# FULL FLOW
# =========================

def test_full_flow(base_url):
    res = requests.post(base_url, json={"name": "Flow", "age": 20})
    student = res.json()

    requests.put(base_url, json={"id": student["id"], "name": "Updated", "age": 30})

    res = requests.get(f"{base_url}/{student['id']}")
    assert res.json()["name"] == "Updated"

    requests.delete(f"{base_url}/{student['id']}")

    res = requests.get(f"{base_url}/{student['id']}")
    assert res.status_code == 404