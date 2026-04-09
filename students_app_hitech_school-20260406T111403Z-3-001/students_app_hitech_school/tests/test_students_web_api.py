from unittest import TestCase
from unittest.mock import patch, Mock
import students_app_hitech_school.app.service as service
from students_app_hitech_school.app.service import ServiceError

class TestStudentWebApi(TestCase):

    # =========================
    # GET STUDENT
    # =========================
    @patch("students_app_hitech_school.app.service.get_student")
    def test_get_student_positive(self, mock_get_student: Mock):
        mock_get_student.return_value = {'id': 1, 'name': 'Mock Student', 'age': 20}
        result = service.get_student(1)
        self.assertEqual(result['id'], 1)
        mock_get_student.assert_called_once_with(1)

    @patch("students_app_hitech_school.app.service.get_student")
    def test_get_student_not_found(self, mock_get_student: Mock):
        mock_get_student.side_effect = KeyError("not found")
        with self.assertRaises(KeyError):
            service.get_student(999999)
        mock_get_student.assert_called_once_with(999999)

    # =========================
    # ADD STUDENT - Positive
    # =========================
    @patch("students_app_hitech_school.app.service.add_student")
    def test_add_student_valid_ages(self, mock_add_student: Mock):
        mock_add_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        for age in [18, 30, 120]:
            result = service.add_student({'name': 'Valid Student', 'age': age})
            self.assertEqual(result['id'], 101)
        self.assertEqual(mock_add_student.call_count, 3)

    @patch("students_app_hitech_school.app.service.add_student")
    def test_add_student_name_variants(self, mock_add_student: Mock):
        mock_add_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        names = ["Danny Parry", "Sam Kelly Jackson", "Matty", "L", "Danny", "DaNNy", "danny student", "Anne-Marie", "J.K. Rowling", "O&Connor"]
        for name in names:
            result = service.add_student({'name': name, 'age': 25})
            self.assertEqual(result['id'], 101)
        self.assertEqual(mock_add_student.call_count, len(names))

    # =========================
    # ADD STUDENT - Negative
    # =========================

    @patch("students_app_hitech_school.app.service.add_student")
    def test_add_student_invalid_cases(self, mock_add_student: Mock):
        # Too young / too old / missing data / wrong types
        mock_add_student.side_effect = ServiceError("add failed")
        invalid_cases = [
            {'name': 'Invalid Age', 'age': 17},
            {'name': 'Invalid Age', 'age': 121},
        ]
        for case in invalid_cases:
            with self.assertRaises(ServiceError):
                service.add_student(case)

        # Name missing / age missing / wrong types
        mock_add_student.side_effect = TypeError("missing or wrong type")
        invalid_cases = [
            {'name': ''}, 
            {'age': 25}, 
            {'name': 123, 'age': 25}, 
            {'name': 'Test', 'age': 'twenty'}
        ]
        for case in invalid_cases:
            with self.assertRaises(TypeError):
                service.add_student(case)

    # =========================
    # UPDATE STUDENT
    # =========================
    @patch("students_app_hitech_school.app.service.update_student")
    def test_update_student_positive(self, mock_update_student: Mock):
        mock_update_student.return_value = {'name': 'Updated', 'age': 30, 'id': 101}
        student = {'name': 'Updated', 'age': 30, 'id': 101}
        result = service.update_student(student)
        self.assertEqual(result['name'], 'Updated')
        mock_update_student.assert_called_once_with(student)

    @patch("students_app_hitech_school.app.service.update_student")
    def test_update_student_invalid(self, mock_update_student: Mock):
        mock_update_student.side_effect = AssertionError("invalid")
        invalid_students = [
            {'name': '', 'age': 40, 'id': 101},
            {'name': None, 'age': 25, 'id': 101},
            {'name': 123, 'age': 25, 'id': 101},
            {'name': 99.3, 'age': 25, 'id': 101},
            {'name': 'Test', 'age': 4, 'id': 101},
            {'name': 'Test', 'age': 145, 'id': 101},
            {'name': 'Test', 'age': -2, 'id': 101}
        ]
        for student in invalid_students:
            with self.assertRaises(AssertionError):
                service.update_student(student)
        self.assertEqual(mock_update_student.call_count, len(invalid_students))

    # =========================
    #  DELETE STUDENT
    # =========================
    @patch("students_app_hitech_school.app.service.delete_student")
    def test_delete_student_positive(self, mock_delete_student: Mock):
        mock_delete_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        for student_id in [1, 10000]:
            result = service.delete_student(student_id)
            self.assertEqual(result['id'], 101)
        self.assertEqual(mock_delete_student.call_count, 2)

    @patch("students_app_hitech_school.app.service.delete_student")
    def test_delete_student_invalid(self, mock_delete_student: Mock):
        mock_delete_student.side_effect = ServiceError("delete failed")
        for student_id in [-1, "abc"]:
            with self.assertRaises(ServiceError):
                service.delete_student(student_id)
        self.assertEqual(mock_delete_student.call_count, 2)