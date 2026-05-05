import pytest  # ספריית בדיקות מתקדמת (אלטרנטיבה ל-unittest)
from students_app_hitech_school.app import db  # שכבת ה-DB שעליה אנחנו בודקים

# ================= FIXTURES ================= #

@pytest.fixture(autouse=True)  # fixture שרץ אוטומטית לפני כל טסט
def clear_db():
    """
    מאפס את ה-DB לפני כל טסט
    """
    db._clear_db()  # מנקה את הדאטה כדי שכל טסט יתחיל נקי


@pytest.fixture
def sample_student():
    """
    יוצר תלמיד אחד בסיסי לכל טסט שצריך
    ומנקה אותו בסוף הטסט
    """

    # Arrange - יצירת תלמיד לבדיקה
    student = db.add_student({"name": "PyTest User", "age": 25})

    yield student  # מחזיר את הסטודנט לטסט (עצירה זמנית של הפונקציה כאן)

    # אחרי שהטסט נגמר - cleanup
    try:
        db.delete_student(student["id"])  # ניסיון למחוק
    except Exception:
        pass  # אם כבר נמחק - לא נקרוס


# ================= CREATE ================= #

# מריץ את אותו טסט כמה פעמים עם נתונים שונים
@pytest.mark.jira_key("SAFP-13")
@pytest.mark.parametrize("student_test", [
    pytest.param({"name":"Leo", "age": 18}, id="min input"),
    pytest.param({"name":"Ben Harris", "age": 120}, id="high input"),
    pytest.param({"name":"avi", "age": 30}, id="normal input"),
])
def test_safp_13_add_student_valid(student_test):

    # Act - מוסיף תלמיד
    added = db.add_student(student_test)

    # Assert - בדיקות
    assert "id" in added  # נוצר ID
    assert added["name"] == student_test["name"]  # שם נשמר נכון
    assert added["age"] == student_test["age"]  # גיל נשמר נכון


@pytest.mark.jira_key("SAFP-13")
@pytest.mark.parametrize("student_test",[
    pytest.param({"name": "A", "age":"twenty"}, id="invalid age"),  # גיל לא מספר
    pytest.param({"name":"A"}, id="missing age"),  # חסר גיל
])
def test_safp_13_add_student_invalid(student_test):

    # מצפים לשגיאה
    with pytest.raises(Exception):
        db.add_student(student_test)


# ================= READ ================= #

@pytest.mark.jira_key("SAFP-16")
def test_safp_16_get_student(sample_student):

    # Act - שליפה לפי ID
    result = db.get_student(sample_student["id"])

    # Assert - בדיקה שהתוצאה זהה למה שיצרנו
    assert result == sample_student

@pytest.mark.jira_key("SAFP-16")
@pytest.mark.parametrize("s_id", [100,-200,"123"])  # ID לא תקינים
def test_safp_16_get_student_negative(s_id):

    # מצפים לשגיאה
    with pytest.raises(Exception):
        db.get_student(s_id)


# ================= UPDATE ================= #

@pytest.mark.jira_key("SAFP-14")
def test_safp_14_update_student(sample_student):

    # Act - עדכון תלמיד קיים
    updated = db.update_student(
        {"id": sample_student["id"] ,"name":"Harry", "age":28}
    )

    # Assert - בדיקה שהעדכון הצליח
    assert updated["id"] == sample_student["id"]  # אותו ID
    assert updated["name"] == "Harry"  # שם חדש
    assert updated["age"] == 28  # גיל חדש


@pytest.mark.jira_key("SAFP-14")
def test_safp_14_update_non_existing():

    # מנסים לעדכן תלמיד שלא קיים
    with pytest.raises(Exception):
        db.update_student({"id": 999, "name": "X", "age": 20})


# ================= DELETE ================= #

@pytest.mark.jira_key("SAFP-15")
def test_safp_15_delete_student(sample_student):

    # Act - מחיקה
    deleted = db.delete_student(sample_student["id"])

    # Assert - בדיקה שנמחק נכון
    assert deleted["id"] == sample_student["id"]

    # בדיקה שהוא באמת לא קיים יותר
    with pytest.raises(Exception):
        db.get_student(sample_student["id"])

@pytest.mark.jira_key("SAFP-15")
@pytest.mark.parametrize("s_id", [888, -1])  # ID לא תקינים
def test_safp_15_delete_student_negative(s_id):

    # מצפים לשגיאה
    with pytest.raises(Exception):
        db.delete_student(s_id)


# ================= FULL FLOW ================= #

def test_full_flow():

    # CREATE - יצירת תלמיד
    student = db.add_student({"name": "Flow", "age": 22})

    # UPDATE - עדכון תלמיד
    updated = db.update_student({
        "id": student["id"],
        "name": "Flow Updated",
        "age": 23
    })

    # בדיקות על העדכון
    assert updated["name"] == "Flow Updated"
    assert updated["age"] == 23

    # DELETE - מחיקה
    db.delete_student(updated["id"])

    # VERIFY DELETE - בדיקה שהוא באמת נמחק
    with pytest.raises(Exception):
        db.get_student(updated["id"])