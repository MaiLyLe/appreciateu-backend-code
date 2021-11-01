from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

"""Part of this code is taken from https://www.udemy.com/course/django-python-advanced/"""


def sample_user(email="student@test.com",
                password="password123",
                name="some name"):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password=password,
                                                name=name)


def sample_user_second(email="test2@test2.com",
                       password="password123",
                       name="some name2"):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password=password,
                                                name=name)


def sample_user_third(email="test3@test3.com",
                      password="password123",
                      name="some name3"):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password=password,
                                                name=name)


def sample_user_fourth(email="test4@test3.com",
                       password="password123",
                       name="some name4"):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password=password,
                                                name=name)


def sample_user_fifth(email="test5@test3.com",
                      password="password123",
                      name="some name5"):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password=password,
                                                name=name)


def sample_user_dynamic_email(email):
    """Create sample user for tests"""
    return get_user_model().objects.create_user(email=email,
                                                password="password123",
                                                name="some name")


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "94mailyle2@gmail.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_new_user_email(self):
        """Test normalization for new user email"""
        email = "test@BLABLA.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password="123test"
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test whether error is raised when no email"""
        user_number_before = get_user_model().objects.count()
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                password="1234Test"
            )
        user_number_after = get_user_model().objects.count()
        self.assertEqual(user_number_before, user_number_after)

    def test_create_new_super_user(self):
        """Test creating new super user"""
        user = get_user_model().objects.create_superuser(
            email="test@hello.com",
            password="testblabla123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_institute_name(self):
        """Test the institute string representation"""
        institute = models.Institute.objects.create(
            name='Fachbereich 1'
        )
        self.assertEqual(str(institute), institute.name)

    def test_field_of_studies_name(self):
        """Test the field of studies string representation"""
        institute = models.Institute.objects.create(
            name='Fachbereich 1'
        )
        field_of_studies = models.FieldOfStudies.objects.create(
            name='Lehramt Kunst',
            institute=institute
        )
        self.assertEqual(str(field_of_studies), field_of_studies.name)

    def test_message_sender_receiver_connection(self):
        """Tests whether sender and receiver are correctly connected by message
        """
        sender = sample_user()
        receiver_prof = sample_user_second()
        receiver_prof.is_professor = True
        receiver_prof.save()
        receiver_student = sample_user_third()
        receiver_student.is_student = True
        receiver_student.save()
        message_1_text = "You are awesome"
        message_2_text = "I love your classes."
        message_3_text = "Thanks for the notes."
        first_message = models.Message.objects.create(text=message_1_text,
                                                      sender=sender,
                                                      receiver=receiver_prof)
        models.Message.objects.create(text=message_2_text,
                                      sender=sender,
                                      receiver=receiver_prof)
        models.Message.objects.create(text=message_3_text,
                                      sender=sender,
                                      receiver=receiver_student)
        self.assertEqual(str(first_message), first_message.text)
        self.assertEqual(sender.messages_sent.all().count(), 3)
        self.assertEqual(sender.messages_received.all().count(), 0)
        self.assertEqual(receiver_prof.messages_received.all().count(), 2)
        self.assertEqual(receiver_prof.messages_sent.all().count(), 0)
