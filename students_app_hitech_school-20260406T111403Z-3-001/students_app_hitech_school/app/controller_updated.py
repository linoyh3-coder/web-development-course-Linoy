import service
from flask import Flask, jsonify, request

students_app = Flask(__name__)


# ==================================
# פונקציות עזר (Utility Functions)
# ==================================

def normalize_student(student):
    # המרה של שדות מספריים לטיפוסים מתאימים (int)
    # נועד למנוע בעיות של קלט מסוג string מה-JSON
    if "id" in student:
        student["id"] = int(student["id"])
    if "age" in student:
        student["age"] = int(student["age"])


def validate_student(student):
    # בדיקת תקינות נתוני תלמיד לפני שמירה או עדכון

    name = student.get("name", "")
    age = student.get("age")

    # בדיקה כי שם התלמיד קיים ובאורך מינימלי של 2 תווים
    if not name or len(name) < 2:
        raise service.ServiceError("Invalid name")

    # בדיקה כי גיל התלמיד נמצא בטווח התקין (18 עד 120)
    if age is None or age < 18 or age > 120:
        raise service.ServiceError("Invalid age")


# ================= ROUTES ================= #

@students_app.route("/")
def home():
    return students_app.send_static_file("index.html")


# ---------- קבלת כל התלמידים ----------

@students_app.route("/students", methods=["GET"])
def get_students():
    return jsonify(service.get_students()), 200


#
# ---------- קבלת תלמיד לפי מזהה ----------
@students_app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        student = service.get_student(student_id)
        return jsonify(student), 200
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


# ---------- הוספת תלמיד חדש ----------

@students_app.route("/students", methods=["POST"])
def add_student():
    student = request.get_json()
    normalize_student(student)

    try:
        validate_student(student)
        student = service.add_student(student)
        return jsonify(student), 201
    except service.ServiceError as e:
        return jsonify({"message": str(e)}), 400


# ---------- עדכון תלמיד (גרסה לפי גוף הבקשה) ----------

@students_app.route("/students", methods=["PUT"])
def update_student_by_body():
    student = request.get_json()
    normalize_student(student)

    try:
        validate_student(student)
        updated = service.update_student(student)
        return jsonify(updated), 200
    except service.ServiceError as e:
        return jsonify({"message": str(e)}), 400
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


# ---------- עדכון תלמיד (גרסה REST עם מזהה ב-URL) ----------

@students_app.route("/students/<int:student_id>", methods=["PUT"])
def update_student_by_id(student_id):
    student = request.get_json()
    normalize_student(student)

    # שיוך מזהה מהנתיב לאובייקט התלמיד
    student["id"] = student_id

    try:
        validate_student(student)
        updated = service.update_student(student)
        return jsonify(updated), 200
    except service.ServiceError as e:
        return jsonify({"message": str(e)}), 400
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


# ---------- מחיקת תלמיד ----------
@students_app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        student = service.delete_student(student_id)
        return jsonify(student), 200
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


# ================= הרצת השרת ================= #

if __name__ == "__main__":
    students_app.run(debug=True)