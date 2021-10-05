from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings
import uuid
import os

def user_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/userimage/', filename)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves new user"""
        if not email:
            raise ValueError("User must register with email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        if not email:
            raise ValueError("User must register with email address")
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    google_email = models.CharField(max_length=255, blank=True)
    google_last_updated = models.DateTimeField(default=now)
    is_professor = models.BooleanField(default=False)
    is_university_administrator = models.BooleanField(default=False)
    avatar_num = models.CharField(max_length=3, default="1")
    user_image = models.ImageField(null=True, upload_to=user_image_file_path)
    objects = UserManager()
    USERNAME_FIELD = "email"


class Institute(models.Model):
    """Represents department that includes multiple similar fields of studies"""
    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name


class FieldOfStudies(models.Model):
    """Represents a specific direction of 
    studies with various courses matching this field"""
    name = models.CharField(max_length=1000, unique=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class GoogleContact(models.Model):
    """Represents a google connection between two users"""
    last_updated = models.DateTimeField(default=now, blank=True)
    contact_owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='google_identity',
                                      null=True,
                                      on_delete=models.CASCADE)
    owned_contact = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='owned_google_contact',
                                      null=True,
                                      on_delete=models.CASCADE)

    def __str__(self):
        return self.contact_owner.email


class Student(models.Model):
    """Model accompanying a user object if user is student"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                )
    field_of_studies = models.ForeignKey(FieldOfStudies,
                                         on_delete=models.CASCADE, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True)
    entry_semester = models.DateTimeField(null=True, blank=True)
    approx_exit_semester = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.name


class Course(models.Model):
    """Model representing a university course with one professor and many students"""
    field_of_studies = models.ForeignKey(FieldOfStudies,
                                         on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000)
    professor = models.ForeignKey('Professor',
                                  on_delete=models.PROTECT, blank=True, null=True, default=None)
    students = models.ManyToManyField(Student, blank=True, default=None)

    def __str__(self):
        return self.name


class Professor(models.Model):
    """Model representing a professor with one connected user object"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    field_of_studies = models.ForeignKey(FieldOfStudies,
                                         on_delete=models.CASCADE, null=True)
    area_of_expertise = models.CharField(max_length=1000)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.name


class UniversityAdministrator(models.Model):
    """Model representing a uni administrator with one connected user object, not used so far"""
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE
                                )
    institute = models.ForeignKey(Institute,
                                  on_delete=models.CASCADE, null=True)
    part_of_institute = models.BooleanField(default=False)
    profession_description = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.user.name


class Message(models.Model):
    """Model representing a message with a sender and a receiver that is a user"""
    text = models.CharField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=False, default=now)
    thanked = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='messages_sent',
                               on_delete=models.PROTECT)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='messages_received',
                                 on_delete=models.PROTECT)
    is_positive = models.BooleanField(default=False)
    avatar_num = models.CharField(max_length=3, default="1")

    def __str__(self):
        return self.text
