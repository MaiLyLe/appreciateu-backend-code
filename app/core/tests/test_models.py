from django.test import TestCase
from django.contrib.auth import get_user_model


# def sample_user(email = "test@test.com",
#                 password = "password123",
#                 name = "some name"):
#     """Create sample user"""
#     return get_user_model().objects.create_user(email = email,
#                                                 password = password,
#                                                 name = name)

class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "94mailyle@gmail.com"
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
