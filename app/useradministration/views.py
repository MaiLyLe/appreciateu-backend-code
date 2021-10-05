from rest_framework import generics, mixins, viewsets, status, views
import json
from .serializers import UserRegistrationSerializer,\
                         CreateProfessorSerializer,\
                         CreateStudentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from useradministration.serializers import InstituteSerializer,\
                                           FieldOfStudiesSerializer,\
                                           CourseSerializer,\
                                           PhotoUploadSerializer
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from core.models import Institute, FieldOfStudies, Course, Student, Professor



class InstituteListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Lists Insittures in the database"""
    permission_classes = (AllowAny,)
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer

class FieldOfStudiesListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """List Fields Of Studies"""
    permission_classes = (AllowAny,)
    queryset = FieldOfStudies.objects.all()
    serializer_class = FieldOfStudiesSerializer

class FieldOfStudiesListViewFiltered(viewsets.GenericViewSet,
                                     mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin):
    """List Fields Of Studies"""
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
        name = self.request.query_params.get('name', None)
        forprof = self.request.query_params.get('forprof', None)
        queryset = Course.objects.all()
        if forprof is not None and forprof is not None:
            queryset = queryset.filter(professor__isnull=True)
        if name is not None and name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset 


class CustomUserRateThrottle(UserRateThrottle):
    rate= '1/second'


class CreateUserWithRoleAndAddCoursesView(viewsets.ModelViewSet):
    """Create Courses by Professor"""
    permission_classes = (AllowAny,)

    @action(methods=['post'], detail=False, parser_classes=(FormParser, MultiPartParser, JSONParser), throttle_classes=[CustomUserRateThrottle])
    def create_user_with_role_and_courses(self, request, pk=None, url_path='create-user-with-role-and-courses'):
        """Creates user with role and courses"""
        
        print(request.data['main'])
        req_main = json.loads(request.data['main']) 
        #print(request.data['user_image'])
        user = req_main['user']
        user_exists = get_user_model().objects.filter(email=user['email']).exists()

        if user_exists is False: 
            serialized_user = UserRegistrationSerializer(data=user)
            if serialized_user.is_valid():
                created_user = get_user_model().objects.create_user(
                    **user
                )
            else:
                return Response({"message": serialized_user.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            is_professor = user['is_professor']

            if 'user_image' in request.data.keys():
                user_image_dict = {"user_image": request.data['user_image']}
                serialized_image = PhotoUploadSerializer(created_user, data=user_image_dict, partial=True)
                if serialized_image.is_valid():
                    serialized_image.save()
                    return Response({"detail": "ok"}, status=status.HTTP_204_NO_CONTENT)
                return Response(serialized_image.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "User image could not be uploaded."}, status=status.HTTP_400_BAD_REQUEST)

            if is_professor is True:
                professor_data = req_main['professor']
                serialized_prof = CreateProfessorSerializer(data=professor_data)
                if serialized_prof.is_valid():
                    field_of_studies = FieldOfStudies.objects.get(id=professor_data['field_of_studies'])
                    institute = Institute.objects.get(id=professor_data['institute'])
                    prof = Professor.objects.create(field_of_studies=field_of_studies,
                                                    institute=institute,
                                                    user=created_user)
                    created_user.professor = prof
                    created_user.save() 
                else:
                    return Response({"message": "Professor account could not not be created."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                student_data = req_main['student']
                serialized_student = CreateStudentSerializer(data=student_data)
                if serialized_student.is_valid():
                    field_of_studies = FieldOfStudies.objects.get(id=student_data['field_of_studies'])
                    institute = Institute.objects.get(id=student_data['institute'])
                    entry_semester = student_data["entry_semester"]
                    approx_exit_semester = student_data["approx_exit_semester"]
                    student = Student.objects.create(field_of_studies=field_of_studies,
                                                     institute=institute,
                                                     entry_semester=entry_semester,
                                                     approx_exit_semester=approx_exit_semester,
                                                     user=created_user)
                else:
                    return Response({"message": "Student account could not not be created."},
                                    status=status.HTTP_400_BAD_REQUEST)
            if is_professor is True and len(req_main['courses']) > 0: 
                for course_id in req_main['courses']:
                    if Course.objects.filter(id=course_id).exists():
                        course = Course.objects.get(id=course_id)
                        course.professor = prof
                        course.save()        
            else:
                if len(req_main['courses']) > 0: 
                    for course_id in req_main['courses']:
                        if Course.objects.filter(id=course_id).exists():
                            student.course_set.add(course_id)

       

        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)