from django.apps import apps
from django.test import TestCase
from django.core.management import call_command


class PopulateDbtTests(TestCase):
    """Test Module for commands that populate db for prototype"""

    def setUp(self):
        call_command('populate_db')

    def test_populate_institute(self):
        """Test whether institute model count is correct and test accuracy
        by checking for one particular entry"""
        engineering_exists = apps.get_model('core', 'Institute').objects.filter(name="Engineering")
        count_all = apps.get_model('core', 'Institute').objects.count()
        self.assertTrue(engineering_exists)
        self.assertEqual(count_all, 3)

    def test_populate_field_of_studies(self):
        """Test whether field of studies model count is correct and test accuracy
        by checking for one particular entry"""
        field_exists = apps.get_model('core', 'FieldOfStudies').objects.filter(name="Informatics")
        count_all = apps.get_model('core', 'FieldOfStudies').objects.count()
        self.assertTrue(field_exists)
        self.assertEqual(count_all, 7)

    def test_populate_user(self):
        """Test whether user model count is correct and test accuracy
        by checking for one particular entry"""
        user_exists = apps.get_model('core', 'User').objects.filter(name="John Wayne",
                                                                    is_student=True)
        count_all = apps.get_model('core', 'User').objects.count()
        self.assertTrue(user_exists)
        self.assertEqual(count_all, 47)

    def test_populate_student(self):
        """Test whether student model count is correct and test accuracy
        by checking for one particular entry"""
        student_exists = apps.get_model('core', 'Student').objects.filter(
            user__email="john.wayne.student@htw.com")
        count_all = apps.get_model('core', 'Student').objects.count()
        self.assertTrue(student_exists)
        self.assertEqual(count_all, 20)

    def test_populate_professor(self):
        """Test whether professor model count is correct and test accuracy
        by checking for one particular entry"""
        professor_exists = apps.get_model('core', 'Professor').objects.filter(
            user__email="ana.summer.professor@htw.com")
        count_all = apps.get_model('core', 'Professor').objects.count()
        self.assertTrue(professor_exists)
        self.assertEqual(count_all, 27)

    def test_populate_course(self):
        """Test whether seminar model count is correct and test accuracy
        by checking for one particular entry"""
        course_exists = apps.get_model('core', 'Course').objects.filter(
            name="Arabic literature in the Middle Ages ")
        count_all = apps.get_model('core', 'Course').objects.count()
        self.assertTrue(course_exists)
        self.assertEqual(count_all, 23)

    def test_add_courses_added_to_student(self):
        """Test whether courses are correctly added to student
        by checking for one particular entry and count of student's courses"""
        student = apps.get_model('core', 'Student').objects.get(
            user__email="john.wayne.student@htw.com")
        student_courses_count = student.course_set.count()
        self.assertEqual(student_courses_count, 6)
