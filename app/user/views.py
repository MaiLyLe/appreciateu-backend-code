from itertools import chain
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Q, Case, When, Value, IntegerField
from user.serializers import UserRegistrationSerializer,\
                             UserSerializer,\
                             ProfessorSerializer,\
                             StudentSerializer
from core.models import Professor, Student, Course, GoogleContact
from .paginators import CustomPagination


def get_message_receivers_senders(user):
    """Retrieves list of all users connected to logged in user by Message model"""
    receivers = user.messages_sent.values_list('receiver', flat=True).distinct()
    senders = user.messages_received.values_list('sender', flat=True).distinct()
    return get_user_model().objects.filter(id__in=list(chain(receivers, senders)))


class UserRetrieveView(viewsets.ModelViewSet):
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
        print(username)
        if username is not None:
            return get_user_model().objects.filter(name__icontains=username)
        return get_user_model().objects.all()


class ProfessorView(viewsets.ModelViewSet):
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

        profs_with_message_connection_to_user = get_message_receivers_senders(user)\
            .filter(is_professor=True)

        google_contacts = GoogleContact.objects.filter(contact_owner=user,
                                                       owned_contact__is_professor=True)
        q = Q(id__in=google_contacts.values_list('owned_contact__professor', flat=True))
        q_0 = Q(id__in=profs_with_message_connection_to_user.values_list('professor__id',
                                                                         flat=True))
        student = user.student
        profs_same_courses_ids = student.course_set.all().order_by().values('professor').distinct()
        profs_same_courses = Professor.objects.filter(id__in=profs_same_courses_ids)
        q_1 = Q(id__in=profs_same_courses)
        profs_same_field = Professor.objects.filter(field_of_studies=student.field_of_studies)
        q_2 = Q(id__in=profs_same_field)
        profs_same_institute = Professor.objects.filter(institute=student.institute)
        q_3 = Q(id__in=profs_same_institute)

        result = Professor.objects.filter(q | q_0 | q_1 | q_2 | q_3).annotate(ordering_type=Case(
            When(q, then=Value(0)),
            When(q_0, then=Value(1)),
            When(q_1, then=Value(2)),
            When(q_2, then=Value(3)),
            When(q_3, then=Value(4)),
            default=Value(-1),
            output_field=IntegerField(),
            )
        ).order_by('ordering_type')

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
        profs_with_message_connection_to_user = get_message_receivers_senders(user)\
            .filter(is_professor=True)
        google_contacts = GoogleContact.objects.filter(contact_owner=user,
                                                       owned_contact__is_professor=True)
        q = Q(id__in=google_contacts.values_list('owned_contact__professor', flat=True))

        q_0 = Q(id__in=profs_with_message_connection_to_user.values_list('professor__id',
                                                                         flat=True))
        professor = user.professor
        profs_same_field = Professor.objects.filter(field_of_studies=professor.field_of_studies)
        q_1 = Q(id__in=profs_same_field)
        profs_same_institute = Professor.objects.filter(institute=professor.institute)
        q_2 = Q(id__in=profs_same_institute)

        profs_rest = Professor.objects.exclude(institute=professor.institute)
        q_3 = Q(id__in=profs_rest)

        result = Professor.objects.filter(q | q_0 | q_1 | q_2 | q_3).annotate(ordering_type=Case(
            When(q, then=Value(0)),
            When(q_0, then=Value(1)),
            When(q_1, then=Value(2)),
            When(q_2, then=Value(3)),
            When(q_3, then=Value(4)),
            default=Value(-1),
            output_field=IntegerField(),
            )
        ).order_by('ordering_type').exclude(id=professor.id)

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = ProfessorSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = ProfessorSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentView(viewsets.ModelViewSet):
    """View for showing students"""
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
        students_with_message_connection_to_user = get_message_receivers_senders(user)\
            .filter(is_student=True)
        google_contacts = GoogleContact.objects.filter(contact_owner=user,
                                                       owned_contact__is_student=True)
        q = Q(id__in=google_contacts.values_list('owned_contact__student', flat=True))

        q_0 = Q(id__in=students_with_message_connection_to_user.values_list('student__id',
                                                                            flat=True))
        student = Student.objects.get(id=user.student.id)
        student_courses = student.course_set.values_list('id', flat=True)
        studs_same_courses_distinct = Student.objects.filter(course__id__in=student_courses)
        q_1 = Q(id__in=studs_same_courses_distinct)
        studs_same_entry_date_and_field = Student.objects \
            .filter(entry_semester=student.entry_semester,
                    field_of_studies=student.field_of_studies)
        q_2 = Q(id__in=studs_same_entry_date_and_field)

        studs_same_field = Student.objects.filter(field_of_studies=student.field_of_studies)\
            .exclude(entry_semester=student.entry_semester)
        q_3 = Q(id__in=studs_same_field)

        studs_same_institute = Student.objects.filter(institute=student.institute)
        q_4 = Q(id__in=studs_same_institute)
        result = Student.objects.filter(q | q_0 | q_1 | q_2 | q_3 | q_4)\
            .annotate(ordering_type=Case(
                When(q, then=Value(0)),
                When(q_0, then=Value(1)),
                When(q_1, then=Value(2)),
                When(q_2, then=Value(3)),
                When(q_3, then=Value(4)),
                When(q_4, then=Value(5)),
                default=Value(-1),
                output_field=IntegerField(),
                )
            ).order_by('ordering_type').exclude(id=student.id)

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
        students_with_message_connection_to_user = get_message_receivers_senders(user)\
            .filter(is_student=True)

        google_contacts = GoogleContact.objects.filter(contact_owner=user,
                                                       owned_contact__is_student=True)
        q = Q(id__in=google_contacts.values_list('owned_contact__student', flat=True))

        q_0 = Q(id__in=students_with_message_connection_to_user.values_list('student__id',
                                                                            flat=True))
        professor = user.professor
        prof_courses = Course.objects.filter(professor=professor.id)
        studs_same_courses = Student.objects.filter(course__id__in=prof_courses)
        q_1 = Q(id__in=studs_same_courses)
        studs_same_field = Student.objects.filter(field_of_studies=professor.field_of_studies)
        q_2 = Q(id__in=studs_same_field)
        studs_same_institute = Student.objects.filter(institute=professor.institute)
        q_3 = Q(id__in=studs_same_institute)
        result = Student.objects.filter(q | q_0 | q_1 | q_2 | q_3).annotate(ordering_type=Case(
            When(q, then=Value(0)),
            When(q_0, then=Value(1)),
            When(q_1, then=Value(2)),
            When(q_2, then=Value(3)),
            When(q_3, then=Value(4)),
            default=Value(-1),
            output_field=IntegerField(),
            )
        ).order_by('ordering_type')

        has_pagination_param = request.GET.get('page', '')
        if not has_pagination_param:
            serializer = StudentSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = StudentSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class VerifyAccessView(APIView):
    """Simple view class only for token verification"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Return a list of all users.
        """
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """View for getting the current user"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Returns essential data for current user"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
