# Views for creating new account or updating account

from rest_framework import mixins, viewsets, status
import json
from .serializers import UserRegistrationSerializer,\
                         CreateUpdateProfessorSerializer,\
                         CreateUpdateStudentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from user_administration.serializers import InstituteSerializer,\
                                           FieldOfStudiesSerializer,\
                                           CourseSerializer,\
                                           PhotoUploadSerializer,\
                                           StudentSerializerWithCourses,\
                                           ProfessorSerializerWithCourses,\
                                           UserUpdateSerializer
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from core.models import Institute, FieldOfStudies, Course, Student, Professor
from django.apps import apps


class StudentWithCoursesView(viewsets.ModelViewSet):
    """Returns currently logged in student user data"""
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = StudentSerializerWithCourses

    @action(detail=False, url_path='data-student')
    def data_student(self, request):
        student = request.user.student
        serializer = self.get_serializer(student)
        return Response(serializer.data)


class ProfessorWithCoursesView(viewsets.ModelViewSet):
    """Returns currently logged in professor user data"""
    permission_classes = (IsAuthenticated,)
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializerWithCourses

    @action(detail=False, url_path='data-professor')
    def data_professor(self, request):
        professor = request.user.professor
        serializer = self.get_serializer(professor)
        return Response(serializer.data)


class InstituteListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Lists Institutes in the database"""
    permission_classes = (AllowAny,)
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer


class FieldOfStudiesListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """List FieldsOfStudies"""
    permission_classes = (AllowAny,)
    queryset = FieldOfStudies.objects.all()
    serializer_class = FieldOfStudiesSerializer


class FieldOfStudiesListViewFiltered(viewsets.GenericViewSet,
                                     mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin):
    """List FieldsOfStudies but filtered by institute"""
    permission_classes = (AllowAny,)
    queryset = FieldOfStudies.objects.all()
    serializer_class = FieldOfStudiesSerializer

    def get_queryset(self):
        """Retrieves query set for user that contains name param"""
        institute_id = self.request.query_params.get('instituteid')
        if institute_id is not None:
            return FieldOfStudies.objects.filter(institute=institute_id)
        return FieldOfStudies.objects.all()


class CoursesListView(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin):
    """List Courses in the database"""
    permission_classes = (AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    paginator = None

    def get_queryset(self):
        """Retrieves Course by name"""
        name = self.request.query_params.get('name', None)
        forprof = self.request.query_params.get('forprof', None)
        queryset = Course.objects.all()
        if forprof is not None and forprof is not None:
            queryset = queryset.filter(professor__isnull=True)
        if name is not None and name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


def perform_save_or_create_role(is_professor, created_user, req_main, is_creating):
    """Performs update or create Student or Professor for user"""
    response_verb = 'created' if is_creating else 'updated'
    if is_professor is True:
        professor_data = None
        if 'professor' in req_main.keys():
            professor_data = req_main['professor']
        if professor_data is not None:
            serialized_prof = CreateUpdateProfessorSerializer(data=professor_data)
            if serialized_prof.is_valid():
                save_or_create_data_in_role(professor_data,
                                            True, is_creating, 'Professor',
                                            created_user)
                return 'success'
            else:
                return Response({"message": f"Professor account could not not be {response_verb}."},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        student_data = None
        if 'student' in req_main.keys():
            student_data = req_main['student']
        if student_data is not None:
            serialized_student = CreateUpdateStudentSerializer(data=student_data)
            if serialized_student.is_valid():
                save_or_create_data_in_role(student_data,
                                            False,
                                            is_creating,
                                            'Student',
                                            created_user)
                return 'success'
            else:
                return Response({"message": f"Student account could not not be {response_verb}."},
                                status=status.HTTP_400_BAD_REQUEST)
    return 'success'

def save_or_create_data_in_role(request_data, is_professor, is_creating, user_role, user):
    """More specific algorithm for updating or creating Professor or Student model"""
    data_dict_base = {}
    data_dict_student = {}
    if 'field_of_studies' in request_data.keys():
        data_dict_base['field_of_studies'] = FieldOfStudies.objects.get(
            id=request_data['field_of_studies'])
        
    if 'institute' in request_data.keys():
        data_dict_base['institute'] = Institute.objects.get(id=request_data['institute'])
    if "entry_semester" in request_data.keys():
        data_dict_student["entry_semester"] = request_data["entry_semester"]
    if "approx_exit_semester" in request_data.keys():
        data_dict_student["approx_exit_semester"] = request_data["approx_exit_semester"]

    result_dict = data_dict_base if is_professor else {**data_dict_base, **data_dict_student}
    if is_creating:
        result_dict = {**result_dict, "user": user}
        user.save()
        apps.get_model('core', user_role).objects.create(**result_dict)
    else:
        apps.get_model('core', user_role).objects.filter(
            user__email=user.email).update(**result_dict)
        user.save()


def perform_save_courses_on_role(is_professor, user, req_main):
    """Saves courses for Student or Professor"""
    if user.is_professor is True and 'courses' in req_main.keys():
        if Course.objects.filter(professor=user.professor).exists():
            user.professor.course_set.clear()
        for course_id in req_main['courses']:
            if Course.objects.filter(id=course_id).exists():
                course = Course.objects.get(id=course_id)
                course.professor = user.professor
                course.save()
    else:
        if 'courses' in req_main.keys():
            user.student.course_set.clear()
            for course_id in req_main['courses']:
                if Course.objects.filter(id=course_id).exists():
                    user.student.course_set.add(course_id)


def save_name_and_email_user(user_data, user):
    """Saves email and name for User if available"""
    if 'name' in user_data.keys():
        user.name = user_data['name']
        user.save()
    if 'email' in user_data.keys():
        user.email = user_data['email']


def perform_user_image_save(request, user, is_creating):
    """Saves user image if avalable for User"""
    if 'user_image' in request.data.keys():
        user.save()
        user_image_dict = {"user_image": request.data['user_image']}
        serialized_image = PhotoUploadSerializer(user,
                                                 data=user_image_dict,
                                                 partial=True)
        if serialized_image.is_valid():
            serialized_image.save()
            return 'success'
        else:
            if is_creating:
                user.delete()
            return Response({"message": "User image could not be uploaded."},
                            status=status.HTTP_400_BAD_REQUEST)
    return 'success'


class CustomUserRateThrottle(UserRateThrottle):
    """Custom throttle class for unauthenticated users"""
    rate = '1/second'


class CreateUserWithRoleAndAddCoursesView(viewsets.ModelViewSet):
    """View for creating user with courses/registering"""
    permission_classes = (AllowAny,)

    @action(methods=['post'],
            detail=False,
            parser_classes=(FormParser, MultiPartParser, JSONParser),
            throttle_classes=[CustomUserRateThrottle])
    def create_user_with_role_and_courses(self,
                                          request,
                                          pk=None,
                                          url_path='create-user-with-role-and-courses'):
        """Endpoint for creating user with role and courses"""
        req_main = json.loads(request.data['main'])
        user = req_main['user']
        user_exists = get_user_model().objects.filter(email=user['email']).exists()

        if user_exists is False:
            serialized_user = UserRegistrationSerializer(data=user)
            if serialized_user.is_valid():
                created_user = get_user_model().objects.create_user(
                    **user
                )
            else:
                return Response(serialized_user.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            is_professor = user['is_professor']
            result_image = perform_user_image_save(request, created_user, True)
            if result_image != 'success':
                return result_image

            result = perform_save_or_create_role(is_professor, created_user, req_main, True)
            if result != 'success':
                return result
            perform_save_courses_on_role(is_professor, created_user, req_main)
        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)


class UpdateUserWithRoleAndAddCoursesView(viewsets.ModelViewSet):
    """View for updating account profile"""
    permission_classes = (IsAuthenticated,)

    @action(methods=['put'],
            detail=False,
            parser_classes=(FormParser, MultiPartParser, JSONParser),
            throttle_classes=[CustomUserRateThrottle])
    def update_user_with_role_and_courses(self,
                                          request, pk=None,
                                          url_path='update-user-with-role-and-courses'):
        """Endpoint for Updating user with role and courses"""
        req_main = json.loads(request.data['main'])
        user_data = req_main['user']
        user = request.user
        serialized_user = UserUpdateSerializer(data=user_data)
        if 'password' in user_data.keys():
            if serialized_user.is_valid():
                save_name_and_email_user(user_data, user)
                if 'password' in user_data.keys():
                    user.set_password(user_data['password'])
                user.save()
            else:
                return Response(serialized_user.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            save_name_and_email_user(user_data, user)
        result_image = perform_user_image_save(request, user, False)
        if result_image != 'success':
            return result_image
    
        result = perform_save_or_create_role(user.is_professor, user, req_main, False)
        if result != 'success':
            return result

        perform_save_courses_on_role(user.is_professor, user, req_main)

        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)
