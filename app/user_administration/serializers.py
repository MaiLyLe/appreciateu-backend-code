from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Student, Professor, Institute, FieldOfStudies, Course


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration or creation"""
    tokens = serializers.SerializerMethodField()

    class Meta:
        """Meta class for User registration serializer"""
        model = get_user_model()
        fields = ('email',
                  'password',
                  'id',
                  'name',
                  'is_professor',
                  'is_student',
                  'user_image',
                  'tokens',
                  'avatar_num')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def get_tokens(self, user):
        """Returns tokens for token authentication"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user update or creation"""
    class Meta:
        """Meta class for User update serializer without email as unique field"""
        model = get_user_model()
        fields = ('email',
                  'password',
                  'id',
                  'name',
                  'is_professor',
                  'is_student',
                  'is_university_administrator',
                  'user_image',
                  'avatar_num')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}


class PhotoUploadSerializer(serializers.ModelSerializer):
    """Serializer for user_image upload for User model"""

    class Meta:
        """Meta class for PhotoUploadSerializer"""
        model = get_user_model()
        fields = ('user_image',)


class GeneralUserSerializer(serializers.ModelSerializer):
    """Serializer for getting basic User info"""

    class Meta:
        """Meta class for GeneralUserSerializer"""
        model = get_user_model()
        """Meta class for User"""
        fields = ('id', 'email', 'name')


class CreateUpdateStudentSerializer(serializers.ModelSerializer):
    """Serializer for creating or updating Student"""
    class Meta:
        """Meta class for CreateUpdateStudentSerializer"""
        model = Student
        """Meta class for CreateStudentSerializer"""
        fields = ('id', 'field_of_studies', 'institute', 'entry_semester', 'approx_exit_semester')


class CreateUpdateProfessorSerializer(serializers.ModelSerializer):
    """Serializer for creating or updating Professor"""

    class Meta:
        """Meta class for CreateUpdateProfessorSerializer"""
        model = Professor
        """Meta class for CreateProfessorSerializer"""
        fields = ('id', 'field_of_studies', 'institute')


class InstituteSerializer(serializers.ModelSerializer):
    """Institute model serializer"""

    class Meta:
        """Meta class for Institute serializer"""
        model = Institute
        fields = ('name', 'id')


class FieldOfStudiesSerializer(serializers.ModelSerializer):
    """FieldOfStudies model serializer"""

    class Meta:
        """Meta class for FieldOfStudies serializer"""
        model = FieldOfStudies
        fields = ['name', 'id']


class CourseSerializer(serializers.ModelSerializer):
    """Course model serializer"""
    field_of_studies = FieldOfStudiesSerializer(required=True)
    professor = CreateUpdateProfessorSerializer(required=True)

    class Meta:
        """Meta class for Course serializer"""
        model = Course
        fields = ['name', 'field_of_studies', 'professor', 'id']


class StudentSerializerWithCourses(serializers.ModelSerializer):
    """Serializer for getting Student with courses"""
    id = serializers.ReadOnlyField()
    user = UserRegistrationSerializer(required=True)
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)
    courses = CourseSerializer(source="course_set", many=True)

    class Meta:
        """Meta class for Student serializer with courses"""
        model = Student
        fields = ('id',
                  'field_of_studies',
                  'institute', 'user',
                  'entry_semester',
                  'approx_exit_semester',
                  'courses')


class ProfessorSerializerWithCourses(serializers.ModelSerializer):
    """Serializer for getting Professor with courses"""
    id = serializers.ReadOnlyField()
    user = UserRegistrationSerializer(required=True)
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)
    taught_courses = CourseSerializer(source="course_set", many=True)

    class Meta:
        """Meta class for Professor serializer with courses"""
        model = Professor
        fields = ('id',
                  'field_of_studies',
                  'institute',
                  'user',
                  'taught_courses')
