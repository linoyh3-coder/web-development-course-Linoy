from unittest import TestCase
from unittest.mock import patch, Mock

import app.service
from app.service import ServiceError
from app import service


class TestService(TestCase):

    # ============== Get Student - Positive Tests ============== #

    # {'id': 1, 'name': 'John Doe', 'age': 20}
    @patch("app.service.db.get_student")
    def test_get_student_positive(self, mock_get_student: Mock):
        # AAA
        # Arrange - set up the mock object
        mock_get_student.return_value = {'id': 1, 'name': 'Mock Student'}
        # Act - use the mock
        result = service.get_student(1)
        # Assert
        self.assertEqual({'id': 1, 'name': 'Mock Student'}, result)
        # Validation - make sure we actually used the mock
        mock_get_student.assert_called_once_with(1)

    # ============== Get Student - Negative Tests =============== #

    @patch("app.service.db.get_student")
    def test_get_student_negative(self, mock_get_student: Mock):
        # arrange
        mock_get_student.side_effect = KeyError("not found: 1")
        # act, assert
        self.assertRaises(KeyError, service.get_student, 111)
        # Validation - make sure we actually used the mock
        mock_get_student.assert_called_once_with(111)

    # ============== Add Student - Positive Tests =============== #

    @patch("app.service.db.add_student")
    def test_add_student_positive(self, mock_add_student: Mock):
        # arrange
        mock_add_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}

        # create students with age cases
        students = [
            {'name': 'Mock Student', 'age': 18, 'id': 101},
            {'name': 'Mock Student', 'age': 30, 'id': 101},
            {'name': 'Mock Student', 'age': 120, 'id': 101}]

        for student in students:
            # act
            result = service.add_student(student)
            # assert
            self.assertEqual({'name': 'Mock Student', 'age': 25, 'id': 101}, result)

        # validate
        self.assertEqual(3, mock_add_student.call_count)

    @patch("app.service.db.add_student")
    def test_add_student_names_length(self, mock_add_student: Mock):
        mock_add_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        students =[
         {'name': 'Danny Parry', 'age': 25, 'id': 101},
         {'name': 'Sam Kelly Jackson', 'age': 25, 'id': 101},
         {'name': 'Matty', 'age': 25, 'id': 101},
         {'name': 'L', 'age': 25, 'id': 101}
         ]
        for student in students:
            result = service.add_student(student)
            self.assertEqual({'name': 'Mock Student', 'age': 25, 'id': 101}, result)
        self.assertEqual(4, mock_add_student.call_count)

    # ============== Add Student - Negative Tests =============== #

    @patch("app.service.db.add_student")
    def test_add_student_too_old(self, mock_add_student: Mock):
        mock_add_student.side_effect = ServiceError("add student failed")
        self.assertRaises(ServiceError, service.add_student, {'name': 'Mock Student', 'age': 142, 'id': 101})
        mock_add_student.assert_not_called()

    @patch("app.service.db.add_student")
    def test_add_student_too_young(self, mock_add_student: Mock):
        mock_add_student.side_effect = ServiceError("add student failed")
        self.assertRaises(ServiceError, service.add_student, {'name': 'Mock Student', 'age': 11, 'id': 101})
        mock_add_student.assert_not_called()

    @patch("app.service.db.add_student")
    def test_add_student_no_letters(self, mock_add_student: Mock):
        mock_add_student.side_effect = ServiceError("Student name is illegal")
        self.assertRaises(ServiceError, service.add_student, {'name': '', 'age': 11, 'id': 101})
        mock_add_student.assert_not_called()

    # ============== Update Student - Positive Tests =============== #

    @patch("app.service.db.update_student")
    def test_update_student_age_in_range(self, mock_update_student: Mock):
        mock_update_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        students =[
        {'name': 'Danny Parry', 'age': 18, 'id': 101},
        {'name': 'John Nick', 'age': 26, 'id': 89},
        {'name': 'Matty King', 'age': 62, 'id': 3},
        {'name': 'Lona Dean', 'age': 120, 'id': 69}
        ]
        for student in students:
            result = service.update_student(student)
            self.assertEqual({'name': 'Mock Student', 'age': 25, 'id': 101}, result)
        self.assertEqual(4, mock_update_student.call_count)

    @patch("app.service.db.update_student")
    def test_Student_must_have_a_name_with_minimum_length(self, mock_update_student: Mock):
        mock_update_student.return_value = {'name': 'Mock Student', 'age': 25, 'id': 101}
        student = {'name': 'M', 'age': 25, 'id': 101}
        result = service.update_student(student)
        self.assertEqual({'name': 'Mock Student', 'age': 25, 'id': 101}, result)
        mock_update_student.assert_called_once_with(student)

    # ============== Update Student - Negative Tests =============== #

    @patch("app.service.db.update_student")
    def test_age_is_not_in_the_range(self, mock_update_student: Mock):
        mock_update_student.side_effect = ServiceError("Student age is illegal")
        students = [
            {'name': 'Mock Student', 'age': 4, 'id': 101},
            {'name': 'Mock Student', 'age': 145, 'id': 101},
            {'name': 'Mock Student', 'age': -2, 'id': 101}
        ]
        for student in students:
            self.assertRaises(ServiceError, service.update_student, student)
        mock_update_student.assert_not_called()

    @patch("app.service.db.update_student")
    def test_name_with_no_minimum_length_of_1_letter(self, mock_update_student:Mock):
        mock_update_student.side_effect = ServiceError("Student name is illegal")
        self.assertRaises(ServiceError, service.update_student, {'name': '', 'age': 40, 'id': 101})
        mock_update_student.assert_not_called()










