from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Student, Professor, Institute, FieldOfStudies, Course


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    
    class Meta:
        """Meta class for User serializer"""
        model = get_user_model()
        fields = ('email',
                  'password',
                  'google_email',
                  'name',
                  'is_professor',
                  'user_image',
                  'is_student',
                  'is_university_administrator',
                  'id',
                  'avatar_num',
                  'google_last_updated',
                  'student',
                  'professor',
                  )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}
    
    def to_representation(self, instance):
        """Overridden function to make sure multiple GoogleContact objects can be saved"""
        response = super().to_representation(instance)
        if response['student'] is not None:
            response['student'] = StudentSerializerWithoutUser(instance.student).data

        if response['professor'] is not None:
            response['professor'] = ProfessorSerializerWithoutUser(instance.professor).data
        return response


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration or creation"""
    is_student = serializers.BooleanField()
    is_professor = serializers.BooleanField()
    is_university_administrator = serializers.BooleanField()
    tokens = serializers.SerializerMethodField()

    class Meta:
        """Meta class for User registration serializer, not used so far"""
        model = get_user_model()
        fields = ('email',
                  'password',
                  'google_email',
                  'name',
                  'is_professor',
                  'is_student',
                  'is_university_administrator',
                  'tokens',
                  'avatar_num')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def get_tokens(self, obj):
        """Returns tokens for token authentication"""
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        user = get_user_model().objects.create_user(**validated_data)
        user.save()
        update_last_login(None, user)
        return user

    def validate(self, data):
        """Validates user data and does not save data if certain attributes not there"""
        is_student = data['is_student']
        is_professor = data['is_professor']
        is_university_administrator = data['is_university_administrator']

        if not is_student and not is_professor and not is_university_administrator:
            raise serializers.ValidationError("At least one role is required")
        return data


class InstituteSerializer(serializers.ModelSerializer):
    """Institute model serializer"""
    class Meta:
        """Meta class for Institute serializer"""
        model = Institute
        fields = ('name',)


class FieldOfStudiesSerializer(serializers.ModelSerializer):
    """FieldOfStudies model serializer"""
    class Meta:
        """Meta class for FieldOfStudies serializer"""
        model = FieldOfStudies
        fields = ('name'),


class CourseSerializer(serializers.ModelSerializer):
    """Course model serializer"""
    class Meta:
        """Meta class for Course serializer"""
        model = Course
        fields = ('name'),


class StudentSerializerWithoutUser(serializers.ModelSerializer):
    """Student model serializer"""
    id = serializers.ReadOnlyField()
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)

    class Meta:
        """Meta class for Student serializer"""
        model = Student
        fields = ('id', 'field_of_studies', 'institute', 'entry_semester',)


class StudentSerializer(serializers.ModelSerializer):
    """Student model serializer"""
    id = serializers.ReadOnlyField()
    user = UserSerializer(required=True)
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)

    class Meta:
        """Meta class for Student serializer"""
        model = Student
        fields = ('id', 'field_of_studies', 'institute', 'entry_semester', 'user',)


class ProfessorSerializerWithoutUser(serializers.ModelSerializer):
    """Professor model serializer"""
    id = serializers.ReadOnlyField()
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)

    class Meta:
        """Meta class for Professor serializer"""
        model = Professor
        fields = ('id', 'field_of_studies', 'institute', 'area_of_expertise',)


class ProfessorSerializer(serializers.ModelSerializer):
    """Professor model serializer"""
    id = serializers.ReadOnlyField()
    user = UserSerializer(required=True)
    institute = InstituteSerializer(required=True)
    field_of_studies = FieldOfStudiesSerializer(required=True)

    class Meta:
        """Meta class for Professor serializer"""
        model = Professor
        fields = ('id', 'user', 'field_of_studies', 'institute', 'area_of_expertise',)
