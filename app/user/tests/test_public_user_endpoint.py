from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from core import models


CREATE_USER_URL = reverse('user:create')
OBTAIN_TOKEN_URL = reverse('user:token_obtain_pair')
PROF_LIST_FOR_PROF_URL = reverse('user:professors-prof-list-for-prof')
STUDENT_LIST_FOR_PROF_URL = reverse('user:students-student-list-for-prof')

valid_user_creation_payload = {
            'email': 'testtesttesttest@test.com',
            'password': '123testtest',
            'name': 'some name',
            'is_student': True,
        }


class PublicUserEndpointTests(TestCase):
    """Test module for public user requests if user not logged in"""
    def setUp(self):
        """Setup function for test class"""
        self.client = Client()

    def test_creation_of_student_model(self):
        "Tests creation of student model if user is student"
        valid_student_role_user_creation_payload = {**valid_user_creation_payload}
        response = self.client.post(CREATE_USER_URL, valid_student_role_user_creation_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copy_data = response.data.copy()
        copy_data.pop('tokens')
        user = get_user_model().objects.get(**copy_data)
        student_exists = models.Student.objects.filter(user=user).exists()
        professor_exists = models.Professor.objects.filter(user=user).exists()
        university_administrator_exists = models.UniversityAdministrator.objects.filter(
            user=user).exists()
        self.assertTrue(student_exists)
        self.assertFalse(professor_exists)
        self.assertFalse(university_administrator_exists)

    def test_create_valid_user(self):
        """Test creation of valid user"""

        response = self.client.post(CREATE_USER_URL, valid_user_creation_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_there = get_user_model().objects.filter(
            email=valid_user_creation_payload['email']).exists()
        self.assertTrue(user_there)

    def test_no_creation_if_more_than_one_role_true(self):
        """Test creation of user with multiple roles, should not be created"""
        invalid_multi_role_user_creation_payload = {**valid_user_creation_payload,
                                                    'is_professor': True}
        response = self.client.post(CREATE_USER_URL, **invalid_multi_role_user_creation_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_creation_if_no_role(self):
        """Test creation of user with no roles, should not be created"""
        invalid_no_role_user_creation_payload = {**valid_user_creation_payload, 'is_student': False}
        response = self.client.post(CREATE_USER_URL, **invalid_no_role_user_creation_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_user_created_if_password_too_short(self):
        """Test whether user is not created if password too short"""
        password_too_short_payload = {**valid_user_creation_payload, 'password': 'p'}
        response = self.client.post(CREATE_USER_URL, password_too_short_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=valid_user_creation_payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_user_not_authenticated_prof_endpint(self):
        """Test not-authorized response if non-authenticated user hits prof endpoints"""
        response = self.client.post(PROF_LIST_FOR_PROF_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_not_authenticated_student_endpint(self):
        """Test not-authorized response if non-authenticated user hits prof endpoints"""
        response = self.client.post(STUDENT_LIST_FOR_PROF_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
