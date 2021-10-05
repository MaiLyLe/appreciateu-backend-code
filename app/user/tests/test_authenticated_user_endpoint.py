from itertools import chain
from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from core import models


CREATE_USER_URL = reverse('user:create')
OBTAIN_TOKEN_URL = reverse('user:token_obtain_pair')
PROF_LIST_FOR_STUDENT_URL = reverse('user:professors-prof-list-for-students')
PROF_LIST_FOR_PROF_URL = reverse('user:professors-prof-list-for-prof')
STUDENT_LIST_FOR_STUDENT_URL = reverse('user:students-student-list-for-student')
STUDENT_LIST_FOR_PROF_URL = reverse('user:students-student-list-for-prof')


def get_message_receivers_senders(user):
    """Retrieves list of all users connected to logged in user by Message model"""
    receivers = user.messages_sent.values_list('receiver', flat=True).distinct()
    senders = user.messages_received.values_list('sender', flat=True).distinct()
    return get_user_model().objects.filter(id__in=list(chain(receivers, senders)))


def get_index_of_user_by_id(id_value, data):
    """Get index of user in list by id"""
    for count, item in enumerate(data):
        if item['id'] == id_value:
            return count
    return None


class UserIsProfEndpointTests(TestCase):
    """Test fixtures for logged in user that is professor"""

    def setUp(self):
        """Setup function for test class"""
        call_command('populate_db')
        self.client = APIClient()
        self.user = get_user_model().objects.get(email='otto.mueller.professor@htw.com')
        response = self.client.post(
            OBTAIN_TOKEN_URL, {"email": self.user.email, "password": 'somePassword131'},
            format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_response_data_prof_list_for_prof(self):
        """Tests existence and correct order of certain profs in response list
        1st another test prof the prof has sent messages or received messages from:
        bronte.huff.professor@htw.com
        2nd test prof that is in same field of studies
        ana.summer.professor@htw.com
        3rd test prof that is in same institute but not in same field:
        abeni.musa.professor@htw.com
        4th test prof that is not in same insititute:
        Dalila.Soyinka.professor@htw.com
        """
        response = self.client.get(PROF_LIST_FOR_PROF_URL)
        data = response.data

        prof_with_message_connection = models.Professor.objects\
            .get(user__email='bronte.huff.professor@htw.com')
        index_0 = get_index_of_user_by_id(prof_with_message_connection.id, data)
        prof_same_field = models.Professor.objects.get(
            user__email='ana.summer.professor@htw.com')
        index_1 = get_index_of_user_by_id(prof_same_field.id, data)

        prof_same_institute_diff_field = models.Professor.objects.get(
            user__email='abeni.musa.professor@htw.com')
        index_2 = get_index_of_user_by_id(prof_same_institute_diff_field.id, data)

        prof_diff_institute = models.Professor.objects.get(
            user__email='Dalila.Soyinka.professor@htw.com')
        index_3 = get_index_of_user_by_id(prof_diff_institute.id, data)
        self.assertTrue(index_0 < index_1 and index_1 < index_2 and index_2 < index_3)

    def test_response_data_student_list_for_prof(self):
        """Tests existence and correct order of certain profs in response list
        1st test student that the prof has sent messages or received messages from:
        john.wayne.student@htw.com
        2nd test student that is in course taught by logged in prof
        sarah.johnson.student@htw.com
        3rd test student that is in same field but not in any course of prof:
        Ricardo.Martinez.student@htw.com
        4th test student that is in same institute but not in same field:
        Mase.Noboru.student@htw.com
        """
        response = self.client.get(STUDENT_LIST_FOR_PROF_URL)
        data = response.data

        student_with_message_connection = models.Student.objects.get(
            user__email='john.wayne.student@htw.com')
        index_0 = get_index_of_user_by_id(student_with_message_connection.id, data)

        student_in_course_taught_by_prof = models.Student.objects.get(
            user__email='sarah.johnson.student@htw.com')
        index_1 = get_index_of_user_by_id(student_in_course_taught_by_prof.id, data)

        student_same_fied_not_in_course_by_prof = models.Student.objects.get(
            user__email='Ricardo.Martinez.student@htw.com')

        index_2 = get_index_of_user_by_id(student_same_fied_not_in_course_by_prof.id, data)

        student_same_institute_diff_field = models.Student.objects.get(
            user__email='Mase.Noboru.student@htw.com')
        index_3 = get_index_of_user_by_id(student_same_institute_diff_field.id, data)

        self.assertTrue(index_0 < index_1 and index_1 < index_2 and index_2 < index_3)


class UserIsStudentEndpointTests(TestCase):
    """Test fixtures for logged in user that is student"""
    def setUp(self):
        call_command('populate_db')
        self.client = APIClient()
        self.user = get_user_model().objects.get(email='john.wayne.student@htw.com')
        response = self.client.post(
            OBTAIN_TOKEN_URL, {"email": self.user.email, "password": 'somePassword123'},
            format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_response_data_prof_list_for_student(self):
        """Tests existence and correct order of certain professors in response list
        1st test prof the student has sent messages or received messages from:
        Rea.Saunders.professor@htw.com
        2nd test professor teaches course the student is in even if in different institute:
        Hanlala.al-Qasim.professor@htw.com
        3rd test prof is in same field of studies but not direct teacher:
        ana.summer.professor@htw.com
        4th test prof is in same same institute but not direct teacher:
        stewart.little.professor@htw.com
        """
        response = self.client.get(PROF_LIST_FOR_STUDENT_URL)
        data = response.data

        prof_with_message_connection = models.Professor.objects\
            .get(user__email='Rea.Saunders.professor@htw.com')
        index_0 = get_index_of_user_by_id(prof_with_message_connection.id, data)
        prof_enrolled_course = models.Professor.objects.get(
            user__email='Hanlala.al-Qasim.professor@htw.com')
        index_1 = get_index_of_user_by_id(prof_enrolled_course.id, data)
        prof_same_field = models.Professor.objects.get(
            user__email='ana.summer.professor@htw.com')
        index_2 = get_index_of_user_by_id(prof_same_field.id, data)
        prof_same_same_institute = models.Professor.objects.get(
            user__email='stewart.little.professor@htw.com')
        index_3 = get_index_of_user_by_id(prof_same_same_institute.id, data)
        self.assertTrue(index_0 < index_1 and index_1 < index_2 and index_2 < index_3)

    def test_response_data_student_list_for_student(self):
        """Tests existence and correct order of certain students in response list
        1st test another student that the student has sent messages or received messages from:
        sarah.johnson.student@htw.com
        2nd test student that is currently in same course with student
        Alda.Amaral.student@htw.com
        3rd test student not in same course, but in same field and has same entry date:
        Johann.Druenert.student@htw.com
        4th test student is in same field but does not have same entry date:
        Ricardo.Martinez.student@htw.com
        5th test student is in same institute but not in same field
        ramin.oloumi.student@htw.com
        """
        response = self.client.get(STUDENT_LIST_FOR_STUDENT_URL)
        data = response.data

        student_with_message_connection = models.Student.objects.get(
                user__email='sarah.johnson.student@htw.com')
        index_0 = get_index_of_user_by_id(student_with_message_connection.id, data)
        stud_same_course = models.Student.objects.get(
            user__email='Alda.Amaral.student@htw.com')
        index_1 = get_index_of_user_by_id(stud_same_course.id, data)

        stud_same_field_same_entry_date = models.Student.objects.get(
            user__email='Johann.Druenert.student@htw.com')
        index_2 = get_index_of_user_by_id(stud_same_field_same_entry_date.id, data)

        stud_same_field_diff_entry_date = models.Student.objects.get(
            user__email='Ricardo.Martinez.student@htw.com')
        index_3 = get_index_of_user_by_id(stud_same_field_diff_entry_date.id, data)

        stud_same_institute_diff_field = models.Student.objects.get(
            user__email='ramin.oloumi.student@htw.com')
        index_4 = get_index_of_user_by_id(stud_same_institute_diff_field.id, data)

        self.assertTrue(
            index_0 < index_1 and index_1 < index_2 and index_2 < index_3 and index_3 < index_4)
