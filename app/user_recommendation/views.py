from itertools import chain
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Q, Case, When, Value, IntegerField
from .serializers import UserSerializer,\
                         ProfessorSerializer,\
                         StudentSerializer
from core.models import Professor, Student, Course, GoogleContact
from .paginators import CustomPagination
from django.apps import apps


def get_message_receivers_senders(user):
    """Retrieves list of all users connected to logged in user by Message model"""
    receivers = user.messages_sent.values_list('receiver', flat=True).distinct()
    senders = user.messages_received.values_list('sender', flat=True).distinct()
    return get_user_model().objects.filter(id__in=list(chain(receivers, senders)))


def get_unique_merged_queryset(exclude_self_id, model_name, q, q_0, q_1, q_2, q_3, q_4):
    """Merges querysets in specific order
    and removes duplicates if user appears in a later queryset"""
    last_q = None
    if q_4 is not None:
        last_q = q_4
    else:
        last_q = q
    result = apps.get_model('core', model_name).objects.filter(q | q_0 | q_1 | q_2 | q_3 | last_q)\
                 .annotate(ordering_type=Case(
                                                When(q, then=Value(0)),
                                                When(q_0, then=Value(1)),
                                                When(q_1, then=Value(2)),
                                                When(q_2, then=Value(3)),
                                                When(q_3, then=Value(4)),
                                                When(last_q, then=Value(5)),
                                                default=Value(-1),
                                                output_field=IntegerField(),
                                            )).order_by('ordering_type')
    result = result.exclude(id=exclude_self_id) if exclude_self_id else result
    return result


def get_single_user_querysets(is_targeting_professors,
                              user,
                              field_of_studies,
                              institute,
                              user_is_student,
                              student_course_ids):
    """Extracts querysets of users for specific cases, whether user is prof or student or which
    users of a specific role should be recommended"""
    model_name = 'professor' if is_targeting_professors else 'student'
    google_contacts = GoogleContact.objects\
                                   .filter(contact_owner=user,
                                           owned_contact__is_professor=is_targeting_professors,
                                           owned_contact__is_student=not is_targeting_professors)
    google_contacts_Q = Q(id__in=google_contacts.values_list(f'owned_contact__{model_name}',
                                                             flat=True))

    contacts_with_message_connection_to_user = get_message_receivers_senders(user)\
        .filter(is_professor=is_targeting_professors, is_student=not is_targeting_professors)
    messaged_contacts_Q = Q(id__in=contacts_with_message_connection_to_user
                            .values_list(f'{model_name}__id', flat=True))

    same_field_contacts = apps.get_model('core', model_name.capitalize()).objects.filter(
        field_of_studies=field_of_studies)
    same_field_contacts_Q = Q(id__in=same_field_contacts)

    same_institute_contacts = apps.get_model('core', model_name.capitalize())\
                                  .objects.filter(institute=institute)
    same_institute_contacts_Q = Q(id__in=same_institute_contacts)

    base_query_set_dict = {"google_contacts_Q": google_contacts_Q,
                           "messaged_contacts_Q": messaged_contacts_Q,
                           "same_field_contacts_Q": same_field_contacts_Q,
                           "same_institute_contacts_Q": same_institute_contacts_Q}

    if user_is_student:
        if is_targeting_professors:
            same_courses_contacts = Professor.objects.filter(id__in=student_course_ids)
            same_courses_contacts_Q = Q(id__in=same_courses_contacts)
            return {**base_query_set_dict,
                    "same_courses_contacts_Q": same_courses_contacts_Q}
        else:
            student = user.student
            student_courses = student.course_set.values_list('id', flat=True)
            studs_same_courses_distinct = Student.objects.filter(course__id__in=student_courses)
            same_courses_contacts_Q = Q(id__in=studs_same_courses_distinct)

            studs_same_entry_date_and_field = Student.objects \
                .filter(entry_semester=student.entry_semester,
                        field_of_studies=student.field_of_studies)
            same_entry_date_Q = Q(id__in=studs_same_entry_date_and_field)

            return {**base_query_set_dict,
                    "same_courses_contacts_Q": same_courses_contacts_Q,
                    "same_entry_date_Q": same_entry_date_Q}
    else:
        if is_targeting_professors:
            profs_rest = Professor.objects.exclude(institute=institute)
            rest_contacts_Q = Q(id__in=profs_rest)
            return {**base_query_set_dict,
                    "rest_contacts_Q": rest_contacts_Q}
        else:
            prof_courses = Course.objects.filter(professor=user.professor.id)
            studs_same_courses = Student.objects.filter(course__id__in=prof_courses)
            same_courses_contacts_Q = Q(id__in=studs_same_courses)
            return {**base_query_set_dict,
                    "same_courses_contacts_Q": same_courses_contacts_Q}


class UserRetrieveView(viewsets.ModelViewSet):
    """View for retrieving either all users or filtered by name"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    queryset = get_user_model().objects.all()

    def list(self, request):
        """Lists all users or filters specific one with get_queryset"""
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        has_pagination_param = request.GET.get('page', '')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if not has_pagination_param:
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        """Retrieves query set for user that contains name param"""
        username = self.request.query_params.get('name')
        if username is not None:
            return get_user_model().objects.filter(name__icontains=username)
        return get_user_model().objects.all()


class ProfessorRecommendationsView(viewsets.ModelViewSet):
    """Views for showing professors"""
    serializer_class = ProfessorSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    queryset = Professor.objects.all()

    def list(self, request):
        """Lists all profs"""
        queryset = Professor.objects.all()
        serializer = ProfessorSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Retrieves query set for professor that contains name param"""
        username = self.request.query_params.get('name')
        if username is not None:
            return Professor.objects.filter(user__name__icontains=username)
        return []

    @action(detail=False, url_path='professor-list-for-student')
    def prof_list_for_students(self, request):
        """
        Retrieves distinct list for logged in student recommending profs for them to message
        with specific order based on how familiar prof is going to be:
        0th set of profs that user had in Google Contacts - q
        1st set: profs the student has already messaged or received message from - q_0
        2nd set: profs teaching courses student is enrolled in - q_1
        3rd set: profs in same field of studies but not teaching student's courses - q_2
        4th set: profs in same institute but not in same field of studies - q_3
        """
        user = request.user
        if user.is_student is False:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        student = user.student
        profs_same_courses_ids = student.course_set.all().order_by().values('professor').distinct()

        query_sets = get_single_user_querysets(True,
                                               user,
                                               student.field_of_studies,
                                               student.institute,
                                               True,
                                               profs_same_courses_ids)

        result = get_unique_merged_queryset(None,
                                            'Professor',
                                            query_sets['google_contacts_Q'],
                                            query_sets['messaged_contacts_Q'],
                                            query_sets['same_courses_contacts_Q'],
                                            query_sets['same_field_contacts_Q'],
                                            query_sets['same_institute_contacts_Q'],
                                            None)

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = ProfessorSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        page = self.paginate_queryset(result)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='professor-list-for-professor')
    def prof_list_for_prof(self, request):
        """
        Retrieves distinct list for logged in prof recommending profs for them to message
        with specific order based on how familiar prof is going to be:
        0th set of profs that user had in Google Contacts - q
        1st set: profs the logged in prof has already messaged or received message from - q_0
        2nd set: profs in same field of studies - q_1
        3rd set: profs in same institute but not in same field of studies - q_2
        4th set: profs in different institute - q_3
        """
        user = request.user
        if user.is_professor is False:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        professor = user.professor
        query_sets = get_single_user_querysets(True,
                                               user,
                                               professor.field_of_studies,
                                               professor.institute,
                                               False,
                                               None)

        result = get_unique_merged_queryset(professor.id,
                                            'Professor',
                                            query_sets['google_contacts_Q'],
                                            query_sets['messaged_contacts_Q'],
                                            query_sets['same_field_contacts_Q'],
                                            query_sets['same_institute_contacts_Q'],
                                            query_sets['rest_contacts_Q'],
                                            None)

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = ProfessorSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = ProfessorSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentRecommendationsView(viewsets.ModelViewSet):
    """View for showing student recommendations"""
    serializer_class = StudentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        """Retrieves query set for professor that contains name param"""
        username = self.request.query_params.get('name')
        if username is not None:
            return Student.objects.filter(user__name__icontains=username)
        return []

    def list(self, request):
        """Lists all students"""
        queryset = Student.objects.all()
        serializer = StudentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='student-list-for-student')
    def student_list_for_student(self, request):
        """
        Retrieves distinct list for logged in student recommending students for them to message
        with specific order based on how familiar other student is going to be:
        0th set of students that user had in Google Contacts - q
        1st set: students the student has already messaged or received message from - q_0
        2nd set: students in same courses student is enrolled in - q_1
        3rd set: students in same field of studies and with same entry date - q_2
        4th set: students in same field of studies but not with same entry date - q_3
        5th set: students in same institute but not in same field of studies - q_4
        """
        user = request.user
        if user.is_student is False:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        student = user.student
        query_sets = get_single_user_querysets(False,
                                               user,
                                               student.field_of_studies,
                                               student.institute,
                                               True,
                                               None)

        result = get_unique_merged_queryset(student.id,
                                            'Student',
                                            query_sets['google_contacts_Q'],
                                            query_sets['messaged_contacts_Q'],
                                            query_sets['same_courses_contacts_Q'],
                                            query_sets['same_entry_date_Q'],
                                            query_sets['same_field_contacts_Q'],
                                            query_sets['same_institute_contacts_Q'],
                                            )

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = StudentSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = StudentSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='student-list-for-professor')
    def student_list_for_prof(self, request):
        """
        Retrieves distinct list for logged in prof recommending students for them to message
        with specific order based on how familiar other student is going to be:
        0th set of students that user had in Google Contacts
        1st set: students the student has already messaged or received message from
        2nd set: students in courses the prof teaches currently
        3rd set: students in same field of studies
        4th set: students in same institute but not in same field of studies
        """
        user = request.user
        if user.is_professor is False:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        professor = user.professor
        query_sets = get_single_user_querysets(False,
                                               user,
                                               professor.field_of_studies,
                                               professor.institute,
                                               False,
                                               None)
        result = get_unique_merged_queryset(None,
                                            'Student',
                                            query_sets['google_contacts_Q'],
                                            query_sets['messaged_contacts_Q'],
                                            query_sets['same_courses_contacts_Q'],
                                            query_sets['same_field_contacts_Q'],
                                            query_sets['same_institute_contacts_Q'],
                                            None
                                            )

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = StudentSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = StudentSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
