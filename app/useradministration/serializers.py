from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Student, Professor, Institute, FieldOfStudies, Course

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration or creation"""
    tokens = serializers.SerializerMethodField()

    class Meta:
        """Meta class for User registration serializer, not used so far"""
        model = get_user_model()
        fields = ('email',
                  'password',
                  'id',
                  'name',
                  'is_professor',
                  'is_student',
                  'is_university_administrator',
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

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        self.user = get_user_model().objects.create_user(**validated_data)
        return self.user

    def validate(self, data):
        """Validates user data and does not save data if certain attributes not there"""
        is_student = data['is_student']
        is_professor = data['is_professor']
        # tokens = self.get_tokens(self.user)
        # data["refresh"] = tokens['refessh']
        # data["access"] = tokens['access']
        # data["email"] = self.user.email

        if not is_student and not is_professor:
            raise serializers.ValidationError("At least one role is required")
        return data

class PhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class for PhotoUploadSerializer"""
        model = get_user_model()
        fields = ('user_image',)

class GeneralUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        """Meta class for User registration serializer, not used so far"""
        fields = ('id', 'email', 'name')


class CreateStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        """Meta class for User registration serializer, not used so far"""
        fields = ('id', 'field_of_studies', 'institute', 'entry_semester', 'approx_exit_semester')


class CreateProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        """Meta class for User registration serializer, not used so far"""
        fields = ('id', 'field_of_studies', 'institute')

class InstituteSerializer(serializers.ModelSerializer):
    """Institute model serializer"""

    class Meta:
        """Meta class for Institute serializer"""
        model = Institute
        fields = ('name', 'id')

class FieldOfStudiesSerializer(serializers.ModelSerializer):
    """FieldOfStudies model serializer"""
    institute = InstituteSerializer(required=True)

    class Meta:
        """Meta class for FieldOfStudies serializer"""
        model = FieldOfStudies
        fields = ['name', 'institute', 'id']

class CourseSerializer(serializers.ModelSerializer):
    """Course model serializer"""
    field_of_studies = FieldOfStudiesSerializer(required=True)
    professor = CreateProfessorSerializer(required=True)
    class Meta:
        """Meta class for Course serializer"""
        model = Course
        fields = ['name', 'field_of_studies', 'professor', 'id']










